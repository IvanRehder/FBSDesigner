#!/usr/bin/env python3
"""
FBS core — lógica compartilhada entre o CLI (fbs_design.py) e a
interface gráfica (app_streamlit.py). Sem input()/print() de diálogo.
"""

import anthropic
import json
import time
from pathlib import Path

MODEL   = "claude-opus-4-8"
# effort: vai dentro de output_config={"effort": ...}
# Opções (Opus 4.8): "low" | "medium" | "high" | "xhigh" | "max"
EFFORT      = "high"   # diálogo (F/Be/S)
EFFORT_MISC = "low"    # resumos (tarefa trivial)
OUT_DIR = Path("fbs_out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

SUMMARY_PATH = OUT_DIR / "_summary.json"


# ── persistência ──────────────────────────────────────────────────────────────
def load_summary():
    if SUMMARY_PATH.exists():
        return json.loads(SUMMARY_PATH.read_text())
    return {}

def save_summary(summary):
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

def load_progress(code):
    p = OUT_DIR / f"{code}_progress.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_progress(code, layer, close_text):
    p = OUT_DIR / f"{code}_progress.json"
    data = load_progress(code)
    data[layer] = close_text
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def clear_progress(code):
    p = OUT_DIR / f"{code}_progress.json"
    if p.exists():
        p.unlink()

def append_to_index(layer, label, code, text):
    idx_path = OUT_DIR / "elements_index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"F": [], "Be": [], "S": []}
    idx[layer].append({"label": label, "requirement": code, "text": text})
    idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False))

def save_chat(code, messages):
    (OUT_DIR / f"{code}_chat.json").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False))

def load_chat(code):
    p = OUT_DIR / f"{code}_chat.json"
    return json.loads(p.read_text()) if p.exists() else []

def clear_chat(code):
    p = OUT_DIR / f"{code}_chat.json"
    if p.exists():
        p.unlink()

def extract_closed_layers(client, code, messages, on_retry=None):
    """Extrai do log os fechamentos de F, Be e S. Retorna (dict, err)."""
    prompt = (
        "From this design conversation, output ONLY a JSON object (no prose, "
        "no fences) with the FINAL closed content of each layer:\n"
        '{"function": "<label + full closed Function statement>", '
        '"behaviour": "<label + full closed Behaviour description>", '
        '"structure": "<labels + full closed Structure elements>"}'
    )
    resp = call_with_retry(client, on_retry=on_retry,
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
    return (OUT_DIR / f"{code}.json").exists()

def next_pending_requirement():
    for req in REQUIREMENTS:
        if not requirement_done(req["code"]):
            return req
    return None


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
        f"- Behaviours: 2-3 distinct interaction flows, labeled Be-{r}.<F>.1, "
        f"Be-{r}.<F>.2, ... using the closed F index.\n"
        f"- Structures: 2-3 distinct sets of concrete HMI elements, labeled "
        f"S-{r}.<F>.<Be>.1, ... using the closed F and Be indices.\n\n"
        "Start with the Function candidates now (state the intent back first). "
        "The designer closes the whole requirement at the end."
    )


# ── chamadas de API ───────────────────────────────────────────────────────────
def call_with_retry(client, on_retry=None, **kwargs):
    for attempt in range(5):
        try:
            return client.messages.create(**kwargs)
        except (anthropic.APIConnectionError, anthropic.APITimeoutError):
            wait = 2 ** attempt
            if on_retry:
                on_retry(wait)
            time.sleep(wait)
    raise RuntimeError("Falha de conexão persistente após 5 tentativas.")

def chat_turn(client, system, messages, on_retry=None):
    """Uma rodada de diálogo. messages já deve conter o último turno do usuário."""
    resp = call_with_retry(client, on_retry=on_retry,
        model=MODEL, max_tokens=1500, output_config={"effort": EFFORT},
        system=system, messages=messages,
    )
    return resp.content[0].text

def extract_layer_entries(client, layer_key, code, messages, on_retry=None):
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
    resp = call_with_retry(client, on_retry=on_retry,
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

def summarize_layer(client, text, layer_label, on_retry=None):
    resp = call_with_retry(client, on_retry=on_retry,
        model=MODEL, max_tokens=40, output_config={"effort": EFFORT_MISC},
        messages=[{"role": "user", "content":
            f"In ONE short phrase (max 12 words), title this {layer_label}: {text}"}],
    )
    return resp.content[0].text.strip()

def summarize(client, fbs, on_retry=None):
    resp = call_with_retry(client, on_retry=on_retry,
        model=MODEL, max_tokens=100, output_config={"effort": EFFORT_MISC},
        messages=[{"role": "user", "content":
            "Summarize this FBS decision in ONE short sentence "
            f"(function + key structure choice): {json.dumps(fbs)}"}],
    )
    return resp.content[0].text.strip()


# ── fechamento do requisito ───────────────────────────────────────────────────
def close_requirement(client, req, messages, summary, on_retry=None):
    """Extrai F/Be/S do log, alimenta o índice, grava artefatos.
    Retorna (fbs, warnings)."""
    code = req["code"]
    warnings = []

    layers, err = extract_closed_layers(client, code, messages, on_retry)
    if err:
        return None, [f"extração das camadas: {err} — requisito NÃO salvo"]

    for layer, key in LAYER_INDEX_KEY.items():
        entries, e = extract_layer_entries(client, key, code, messages, on_retry)
        if e:
            warnings.append(f"índice {key}: {e} — completar manualmente")
        for item in entries:
            append_to_index(key, item["label"], code, item["text"])

    mods = " and ".join(req["modalities"])
    fbs = {
        "code": code, "name_en": req["name_en"], "type": req["type"],
        "modalities": req["modalities"],
        "function": layers["function"],
        "function_summary": summarize_layer(client, layers["function"], "Function", on_retry),
        "behaviour": layers["behaviour"],
        "behaviour_summary": summarize_layer(client, layers["behaviour"], "Behaviour", on_retry),
        "structure": layers["structure"],
        "structure_summary": summarize_layer(client, layers["structure"], "Structure", on_retry),
    }
    (OUT_DIR / f"{code}.json").write_text(json.dumps(fbs, indent=2, ensure_ascii=False))
    (OUT_DIR / f"{code}_log.json").write_text(json.dumps(messages, indent=2, ensure_ascii=False))
    (OUT_DIR / f"{code}_summary.md").write_text(
        f"# {code} — {req['name_en']} ({req['type']})\n\n"
        f"**Modalities:** {mods}\n\n"
        f"## Function\n{layers['function']}\n\n"
        f"## Behaviour\n{layers['behaviour']}\n\n"
        f"## Structure\n{layers['structure']}\n"
    )
    summary[code] = summarize(client, fbs, on_retry)
    save_summary(summary)
    clear_chat(code)
    clear_progress(code)
    return fbs, warnings