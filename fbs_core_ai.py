#!/usr/bin/env python3
"""
FBS core — lógica compartilhada entre o CLI (fbs_design.py) e a
interface gráfica (app_streamlit.py). Sem input()/print() de diálogo.
"""

import anthropic
import json
import os
import time
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODEL   = "claude-opus-4-8"
# preço oficial Anthropic, USD por milhão de tokens (fonte: platform.claude.com/docs/pricing)
PRICE_PER_MTOK = {"input": 5.0, "output": 25.0}
# effort: vai dentro de output_config={"effort": ...}
# Opções (Opus 4.8): "low" | "medium" | "high" | "xhigh" | "max"
EFFORT      = "high"   # diálogo (F/Be/S)
EFFORT_MISC = "low"    # resumos (tarefa trivial)
BASE_OUT_DIR = Path(os.environ.get("FBS_OUT_DIR", "out"))
BASE_OUT_DIR.mkdir(parents=True, exist_ok=True)

def current_out_dir():
    """A pasta do designer atual. Vive em st.session_state (isolado por
    sessão de verdade) — NUNCA numa variável global do módulo, porque no
    Streamlit Cloud todos os usuários conectados ao mesmo app compartilham
    o mesmo processo Python, e uma variável global mutável vazaria dados
    de um designer pra sessão de outro."""
    return st.session_state.get("out_dir", BASE_OUT_DIR)

def sanitize_designer_id(designer_id):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in designer_id.strip().lower())

def designer_registered(designer_id):
    safe = sanitize_designer_id(designer_id)
    return (BASE_OUT_DIR / safe / "designer_info.json").exists()

def set_designer(designer_id):
    """Redireciona a pasta do designer atual pra uma subpasta por designer
    (case-insensitive). Chamar antes de qualquer outra função que leia/
    grave dados do designer. Guarda em st.session_state — isolado por
    sessão, ao contrário de uma variável global do módulo."""
    safe = sanitize_designer_id(designer_id)
    d = BASE_OUT_DIR / safe
    d.mkdir(parents=True, exist_ok=True)
    st.session_state.out_dir = d
    return safe

def save_designer_info(info):
    (current_out_dir() / "designer_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False))

SYSTEM_DESCRIPTION = Path("system_description.txt").read_text()
HMI_BASELINE       = Path("hmi_baseline.txt").read_text()
RESPONSE_STYLE     = Path("response_style.txt").read_text()
REQUIREMENTS       = json.loads(Path("requirements.json").read_text())

LAYERS = ["function", "behaviour", "structure"]
LAYER_INDEX_KEY = {"function": "F", "behaviour": "Be", "structure": "S"}

MODALITY_VOCABULARY = """\
Modality vocabulary (use ONLY these; do not introduce others):
- Touch: direct input on a touch-sensitive display (tap, select, drag).
- Keyboard: physical/virtual keyboard and buttons; text and value entry.
- Screen: visual OUTPUT; information rendered on a display.
- Voice-in: INPUT by recognized voice command (ASR / speech-to-command).
- Audio-out: sound OUTPUT from the system (acoustic alert or synthesized speech/TTS).
- Wearable/HMD: head-mounted device (VR/AR/XR). As INPUT: head/eye-tracking, gestures. As OUTPUT: in-visor display.
- Haptic: tactile / force feedback.
"""

def load_summary():
    p = current_out_dir() / "_summary.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}

def save_summary(summary):
    (current_out_dir() / "_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

def load_progress(code):
    p = current_out_dir() / f"{code}_progress.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_progress(code, layer, close_text):
    p = current_out_dir() / f"{code}_progress.json"
    data = load_progress(code)
    data[layer] = close_text
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def clear_progress(code):
    p = current_out_dir() / f"{code}_progress.json"
    if p.exists():
        p.unlink()

def append_to_index(layer, label, code, text):
    idx_path = current_out_dir() / "elements_index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"F": [], "Be": [], "S": []}
    idx[layer].append({"label": label, "requirement": code, "text": text})
    idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False))

def save_chat(code, messages):
    (current_out_dir() / f"{code}_chat.json").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False))

def load_chat(code):
    p = current_out_dir() / f"{code}_chat.json"
    return json.loads(p.read_text()) if p.exists() else []

def clear_chat(code):
    p = current_out_dir() / f"{code}_chat.json"
    if p.exists():
        p.unlink()

def _started_path(code):
    return current_out_dir() / f"{code}_started.txt"

def mark_started(code):
    p = _started_path(code)
    if not p.exists():
        p.write_text(str(time.time()))

def elapsed_wall_s(code):
    p = _started_path(code)
    return round(time.time() - float(p.read_text()), 1) if p.exists() else None

def extract_closed_layers(client, code, messages, on_retry=None, usage_log=None):
    """Extrai do log os fechamentos de F, Be e S. Retorna (dict, err)."""
    prompt = (
        "From this design conversation, output ONLY a JSON object (no prose, "
        "no fences) with the FINAL closed content of each layer, plus a revision "
        "count per layer (how many times a substantively different proposal was "
        "made for that layer before the designer accepted one — 0 if accepted "
        "on the first proposal):\n"
        '{"function": "<label + full closed Function statement>", '
        '"behaviour": "<label + full closed Behaviour description>", '
        '"structure": "<labels + full closed Structure elements>", '
        '"revisions": {"function": <int>, "behaviour": <int>, "structure": <int>}}'
    )
    resp = call_with_retry(client, on_retry=on_retry, usage_log=usage_log,
        model=MODEL, max_tokens=2000, output_config={"effort": EFFORT_MISC},
        system="Return ONLY valid JSON, nothing else.",
        messages=messages + [{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        d = json.loads(raw)
        missing = [k for k in ("function", "behaviour", "structure") if k not in d]
        if missing:
            return None, f"faltando camadas: {missing}"
        return d, None
    except json.JSONDecodeError as e:
        return None, f"parse falhou: {e}"

def requirement_done(code):
    return (current_out_dir() / f"{code}.json").exists()

def next_pending_requirement():
    for req in REQUIREMENTS:
        if not requirement_done(req["code"]):
            return req
    return None


# ── SUS (System Usability Scale, Brooke 1996 — wording original) ─────────────
SUS_ITEMS = [
    ("I think that I would like to use this system frequently", True),
    ("I found the system unnecessarily complex", False),
    ("I thought the system was easy to use", True),
    ("I think that I would need the support of a technical person to be able to use this system", False),
    ("I found the various functions in this system were well integrated", True),
    ("I thought there was too much inconsistency in this system", False),
    ("I would imagine that most people would learn to use this system very quickly", True),
    ("I found the system very cumbersome to use", False),
    ("I felt very confident using the system", True),
    ("I needed to learn a lot of things before I could get going with this system", False),
]

def sus_score(responses):
    total = 0
    for (_, positive), r in zip(SUS_ITEMS, responses):
        total += (r - 1) if positive else (5 - r)
    return round(total * 2.5, 1)

def sus_done():
    return (current_out_dir() / "sus.json").exists()

def save_sus(responses):
    score = sus_score(responses)
    (current_out_dir() / "sus.json").write_text(json.dumps(
        {"responses": responses, "score": score}, indent=2, ensure_ascii=False))
    return score


# ── toy problem (aquecimento, sempre zero IA, precisa de aprovação) ──────────
def load_toy_requirement():
    return json.loads(Path("toy_requirement.json").read_text())

def toy_status():
    p = current_out_dir() / "toy_status.json"
    return json.loads(p.read_text()) if p.exists() else {"submitted": False, "approved": False}

def load_toy_submission():
    p = current_out_dir() / "toy_submission.json"
    return json.loads(p.read_text()) if p.exists() else None

def submit_toy_problem(entries):
    (current_out_dir() / "toy_submission.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    (current_out_dir() / "toy_status.json").write_text(json.dumps(
        {"submitted": True, "approved": False}, indent=2, ensure_ascii=False))

def approve_toy(designer_folder):
    """Usado pelo painel admin, que opera fora do designer 'atual' — por
    isso recebe a pasta explicitamente em vez de depender de current_out_dir()."""
    p = designer_folder / "toy_status.json"
    status = json.loads(p.read_text()) if p.exists() else {"submitted": True, "approved": False}
    status["approved"] = True
    p.write_text(json.dumps(status, indent=2, ensure_ascii=False))

def reopen_toy():
    """Usado pelo próprio designer, na tela de 'aguardando aprovação', pra
    poder editar e reenviar em vez de ficar travado esperando."""
    status = toy_status()
    status["submitted"] = False
    (current_out_dir() / "toy_status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False))


# ── system prompt ─────────────────────────────────────────────────────────────
def fbs_system(prior_summary=None):
    prior_block = ""
    if prior_summary:
        lines = [f"- {code}: {s}" for code, s in prior_summary.items()]
        prior_block = (
            "\n\n=== PRIOR REQUIREMENTS ALREADY DEFINED (for consistency) ===\n"
            + "\n".join(lines)
        )
    return (
        "You are a design engineer assisting in the functional and structural design "
        "of a Multimodal HMI for MUM-T ISR operations, using the Function-Behaviour-"
        "Structure (FBS) ontology.\n\n"
        "Definitions for THIS project:\n"
        "- Function (F): the teleology of the artefact — what it is FOR. It connects "
        "the designer's goals to the artefact's measurable effects. Function must "
        "NOT describe sequence, ordering, guidance logic, confirmation steps, or "
        "any interaction flow — that belongs to Behaviour, not here.\n"
        "- Behaviour (Be): what the artefact DOES — the attributes derivable from "
        "its structure, expressed as the interaction flow that realizes the "
        "function using ONLY the fixed modalities. Provides measurable performance "
        "criteria.\n"
        "- Structure (S): what the artefact CONSISTS OF — its components and their "
        "relationships; the concrete HMI elements that implement the behaviour.\n\n"
        "Cardinality: F, Be and S are NOT 1:1:1 per requirement, and the relationship "
        "isn't purely downward either — a Behaviour can serve multiple Functions, "
        "and a Structure can serve multiple Behaviours/Functions (shared/reused "
        "elements, not duplicated per Function). The dialogue below closes on one "
        "path per layer for tractability, but flag it explicitly when a Be or S "
        "candidate could be shared across Functions rather than being exclusive to "
        "one. Don't preemptively design for reuse in requirements not yet "
        "discussed — flag sharing only when it's relevant to the requirement at "
        "hand. Reuse across the full requirement set gets consolidated later.\n\n"
        "You will discuss ONE layer at a time (Function, then Behaviour, then "
        "Structure) with the human designer. Propose an option, explain your "
        "reasoning briefly, and engage with pushback — if the designer disagrees, "
        "understand their point and either adjust or explain why you'd keep your "
        "suggestion. This is a negotiation, not a one-shot approval. The designer "
        "will say something like 'ok' to close the current layer.\n\n"
        f"{MODALITY_VOCABULARY}\n\n"
        "=== SYSTEM DESCRIPTION ===\n"
        f"{SYSTEM_DESCRIPTION}\n\n"
        f"{HMI_BASELINE}\n\n"
        f"{RESPONSE_STYLE}"
        f"{prior_block}"
    )


# ── prompts de abertura por camada ────────────────────────────────────────────
def opening_prompt(req):
    code = req["code"]
    r = code[1:]
    mods = " and ".join(req["modalities"])
    return (
        f"Requirement {code} ({req['type']}): {req['name_en']}. "
        f"Fixed modalities: {mods}. Intent: {req['intent']}.\n\n"
        "We will design this requirement in three sequential layers, all within "
        "THIS conversation: Function first, then Behaviour, then Structure. "
        "Conduct the sequence yourself — when a layer is agreed, state its final "
        "label clearly and move to the next.\n"
        f"- Functions: propose 2-3 genuinely distinct candidates labeled F-{r}.1, "
        f"F-{r}.2, ... Distinct means each opens a different interaction goal — "
        "not the same goal reworded.\n"
        f"- Behaviours: one distinct interaction idea per fixed modality "
        f"pathway (e.g. one Touch-only, one Keyboard-only), plus a Mixed "
        f"pathway if it adds real value beyond the two. Labeled Be-{r}.<F>.1, "
        f"Be-{r}.<F>.2, ... using the closed F index.\n"
        f"- Structures: 2-3 distinct sets of concrete HMI elements, labeled "
        f"S-{r}.<F>.<Be>.1, ... using the closed F and Be indices.\n\n"
        "Start with the Function candidates now (state the intent back first). "
        "The designer closes the whole requirement at the end."
    )


# ── chamadas de API ───────────────────────────────────────────────────────────
def call_with_retry(client, on_retry=None, usage_log=None, **kwargs):
    start = time.time()
    for attempt in range(5):
        try:
            resp = client.messages.create(**kwargs)
            if usage_log is not None:
                usage_log.append({
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                    "cache_read_tokens": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
                    "cache_write_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0) or 0,
                    "elapsed_s": round(time.time() - start, 2),
                })
            return resp
        except (anthropic.APIConnectionError, anthropic.APITimeoutError):
            wait = 2 ** attempt
            if on_retry:
                on_retry(wait)
            time.sleep(wait)
    raise RuntimeError("Falha de conexão persistente após 5 tentativas.")

def chat_turn(client, system, messages, on_retry=None, usage_log=None):
    """Uma rodada de diálogo. messages já deve conter o último turno do usuário."""
    resp = call_with_retry(client, on_retry=on_retry, usage_log=usage_log,
        model=MODEL, max_tokens=1500, output_config={"effort": EFFORT},
        system=system, messages=messages,
    )
    return resp.content[0].text

def usage_totals(usage_log):
    tin = sum(u["input_tokens"] for u in usage_log)
    tout = sum(u["output_tokens"] for u in usage_log)
    tcache_r = sum(u.get("cache_read_tokens", 0) for u in usage_log)
    tcache_w = sum(u.get("cache_write_tokens", 0) for u in usage_log)
    cost = tin / 1e6 * PRICE_PER_MTOK["input"] + tout / 1e6 * PRICE_PER_MTOK["output"]
    return {
        "calls": len(usage_log),
        "input_tokens": tin,
        "output_tokens": tout,
        "cache_read_tokens": tcache_r,
        "cache_write_tokens": tcache_w,
        "total_tokens": tin + tout,
        "elapsed_s": round(sum(u["elapsed_s"] for u in usage_log), 2),
        "cost_usd": round(cost, 4),
    }

def save_usage(code, usage_log, process_stats=None):
    totals = usage_totals(usage_log)
    if process_stats:
        totals.update(process_stats)
    (current_out_dir() / f"{code}_usage.json").write_text(json.dumps(
        {"calls": usage_log, "totals": totals}, indent=2, ensure_ascii=False))
    return totals

def extract_layer_entries(client, layer_key, code, messages, on_retry=None, usage_log=None):
    label_formats = {
        "F": "F<r>.<f>",
        "Be": "Be<r>.<f>.<be>",
        "S": "S<r>.<f>.<be>.<s>",
    }
    prompt = (
        f"Output ONLY a JSON array (no prose, no markdown fences) listing the "
        f"individual {layer_key} elements just closed. Each item: "
        f'{{"label": "...", "requirement": "{code}", "text": "..."}}. '
        f'Label format: {label_formats[layer_key]}, using the r/f/be/s indices from '
        f"this conversation (r = requirement number without leading zero issues, "
        f"e.g. R01 -> 01). One array item per distinct element (e.g. if 3 "
        f"Behaviours were closed, output 3 items)."
    )
    resp = call_with_retry(client, on_retry=on_retry, usage_log=usage_log,
        model=MODEL, max_tokens=800, output_config={"effort": EFFORT_MISC},
        system="Return ONLY valid JSON, nothing else.",
        messages=messages + [{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return [], f"parse falhou para {layer_key}: {e}"

def summarize_layer(client, text, layer_label, on_retry=None, usage_log=None):
    resp = call_with_retry(client, on_retry=on_retry, usage_log=usage_log,
        model=MODEL, max_tokens=40, output_config={"effort": EFFORT_MISC},
        messages=[{"role": "user", "content":
            f"In ONE short phrase (max 12 words), title this {layer_label}: {text}"}],
    )
    return resp.content[0].text.strip()

def summarize(client, fbs, on_retry=None, usage_log=None):
    resp = call_with_retry(client, on_retry=on_retry, usage_log=usage_log,
        model=MODEL, max_tokens=100, output_config={"effort": EFFORT_MISC},
        messages=[{"role": "user", "content":
            "Summarize this FBS decision in ONE short sentence "
            f"(function + key structure choice): {json.dumps(fbs)}"}],
    )
    return resp.content[0].text.strip()


# ── fechamento do requisito ───────────────────────────────────────────────────
def close_requirement(client, req, messages, summary, on_retry=None, usage_log=None):
    """Extrai F/Be/S do log, alimenta o índice, grava artefatos.
    Retorna (fbs, warnings). usage_log acumula tokens/tempo de toda a
    conversa do requisito (turnos de chat + chamadas de fechamento)."""
    code = req["code"]
    warnings = []
    if usage_log is None:
        usage_log = []

    layers, err = extract_closed_layers(client, code, messages, on_retry, usage_log)
    if err:
        return None, [f"extração das camadas: {err} — requisito NÃO salvo"]

    for layer, key in LAYER_INDEX_KEY.items():
        entries, e = extract_layer_entries(client, key, code, messages, on_retry, usage_log)
        if e:
            warnings.append(f"índice {key}: {e} — completar manualmente")
        for item in entries:
            append_to_index(key, item["label"], code, item["text"])

    mods = " and ".join(req["modalities"])
    fbs = {
        "code": code, "name_en": req["name_en"], "type": req["type"],
        "modalities": req["modalities"],
        "closed_at": time.time(),
        "function": layers["function"],
        "function_summary": summarize_layer(client, layers["function"], "Function", on_retry, usage_log),
        "behaviour": layers["behaviour"],
        "behaviour_summary": summarize_layer(client, layers["behaviour"], "Behaviour", on_retry, usage_log),
        "structure": layers["structure"],
        "structure_summary": summarize_layer(client, layers["structure"], "Structure", on_retry, usage_log),
    }
    (current_out_dir() / f"{code}.json").write_text(json.dumps(fbs, indent=2, ensure_ascii=False))
    (current_out_dir() / f"{code}_log.json").write_text(json.dumps(messages, indent=2, ensure_ascii=False))
    (current_out_dir() / f"{code}_summary.md").write_text(
        f"# {code} — {req['name_en']} ({req['type']})\n\n"
        f"**Modalities:** {mods}\n\n"
        f"## Function\n{layers['function']}\n\n"
        f"## Behaviour\n{layers['behaviour']}\n\n"
        f"## Structure\n{layers['structure']}\n"
    )
    summary[code] = summarize(client, fbs, on_retry, usage_log)
    save_summary(summary)

    process_stats = {
        "user_turns": sum(1 for m in messages if m["role"] == "user"),
        "revisions": layers.get("revisions", {}),
        "wall_clock_s": elapsed_wall_s(code),
    }
    totals = save_usage(code, usage_log, process_stats)
    clear_chat(code)
    clear_progress(code)
    _started_path(code).unlink(missing_ok=True)
    return fbs, warnings


# ── revisão de requisito já fechado ───────────────────────────────────────────
def reopen_requirement(code):
    """Designer decidiu revisar um requisito já fechado. Arquiva o
    fechamento antigo (não perde o dado) e libera o código pra ser refeito.
    Retorna (closed_at antigo, conteúdo antigo de {code}_log.json) — o
    primeiro pra saber quem foi fechado depois, o segundo pra quem quiser
    recarregar o conteúdo anterior pra edição."""
    p = current_out_dir() / f"{code}.json"
    old = json.loads(p.read_text())
    old_closed_at = old.get("closed_at")
    old_log_path = current_out_dir() / f"{code}_log.json"
    old_log = json.loads(old_log_path.read_text()) if old_log_path.exists() else None
    n = 1
    while (current_out_dir() / f"{code}_prev{n}.json").exists():
        n += 1
    p.rename(current_out_dir() / f"{code}_prev{n}.json")
    for suffix in ("_log.json", "_summary.md", "_usage.json"):
        src = current_out_dir() / f"{code}{suffix}"
        if src.exists():
            src.rename(current_out_dir() / f"{code}_prev{n}{suffix}")
    return old_closed_at, old_log

def downstream_affected(code, old_closed_at):
    """Requisitos já fechados depois de `code` (podem ter usado a versão
    antiga dele como parte do contexto de consistência)."""
    if old_closed_at is None:
        return []
    affected = []
    for req in REQUIREMENTS:
        other = req["code"]
        if other == code:
            continue
        p = current_out_dir() / f"{other}.json"
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("closed_at", 0) > old_closed_at:
                affected.append(other)
    return affected