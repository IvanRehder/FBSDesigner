#!/usr/bin/env python3
"""
FBS core — condição controle (sem IA). Fork de fbs_core_ai.py sem o
system prompt de design nem o chat_turn — o único uso do Claude aqui é
extrair/indexar o que o designer já escreveu (close_requirement).
"""

import anthropic
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODEL   = "claude-opus-4-8"
# preço oficial Anthropic, USD por milhão de tokens (fonte: platform.claude.com/docs/pricing)
PRICE_PER_MTOK = {"input": 5.0, "output": 25.0}
# effort: vai dentro de output_config={"effort": ...}
# Opções (Opus 4.8): "low" | "medium" | "high" | "xhigh" | "max"
EFFORT_MISC = "low"    # extração/indexação (tarefa trivial)
OUT_DIR = Path(os.environ.get("FBS_OUT_DIR", "fbs_out"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUIREMENTS = json.loads(Path("requirements.json").read_text())

LAYERS = ["function", "behaviour", "structure"]
LAYER_INDEX_KEY = {"function": "F", "behaviour": "Be", "structure": "S"}

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

def _started_path(code):
    return OUT_DIR / f"{code}_started.txt"

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
    return (OUT_DIR / f"{code}.json").exists()

def next_pending_requirement():
    for req in REQUIREMENTS:
        if not requirement_done(req["code"]):
            return req
    return None


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
    (OUT_DIR / f"{code}_usage.json").write_text(json.dumps(
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
        "function": layers["function"],
        "function_summary": summarize_layer(client, layers["function"], "Function", on_retry, usage_log),
        "behaviour": layers["behaviour"],
        "behaviour_summary": summarize_layer(client, layers["behaviour"], "Behaviour", on_retry, usage_log),
        "structure": layers["structure"],
        "structure_summary": summarize_layer(client, layers["structure"], "Structure", on_retry, usage_log),
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