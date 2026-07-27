#!/usr/bin/env python3
"""
FBS core — condição controle (zero IA). Nenhuma função aqui chama a API
da Anthropic. O designer entra com Function/Behaviour/Structure como
itens estruturados (label + texto), um de cada vez; o encerramento do
requisito só grava o que já foi decidido, sem nenhuma etapa de extração
por modelo.
"""

import json
import os
import time
from pathlib import Path

OUT_DIR = Path(os.environ.get("FBS_OUT_DIR", "fbs_out"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUIREMENTS = json.loads(Path("requirements.json").read_text())
LAYER_INDEX_KEY = {"function": "F", "behaviour": "Be", "structure": "S"}

SUMMARY_PATH = OUT_DIR / "_summary.json"


# ── persistência ──────────────────────────────────────────────────────────────
def load_summary():
    if SUMMARY_PATH.exists():
        return json.loads(SUMMARY_PATH.read_text())
    return {}

def save_summary(summary):
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

def append_to_index(layer, label, code, text):
    idx_path = OUT_DIR / "elements_index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"F": [], "Be": [], "S": []}
    idx[layer].append({"label": label, "requirement": code, "text": text})
    idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False))

def save_manual(code, state):
    (OUT_DIR / f"{code}_manual.json").write_text(json.dumps(state, indent=2, ensure_ascii=False))

def load_manual(code):
    p = OUT_DIR / f"{code}_manual.json"
    return json.loads(p.read_text()) if p.exists() else None

def clear_manual(code):
    p = OUT_DIR / f"{code}_manual.json"
    if p.exists():
        p.unlink()

def requirement_done(code):
    return (OUT_DIR / f"{code}.json").exists()

def next_pending_requirement():
    for req in REQUIREMENTS:
        if not requirement_done(req["code"]):
            return req
    return None


# ── cronometragem de parede ───────────────────────────────────────────────────
def _started_path(code):
    return OUT_DIR / f"{code}_started.txt"

def mark_started(code):
    p = _started_path(code)
    if not p.exists():
        p.write_text(str(time.time()))

def elapsed_wall_s(code):
    p = _started_path(code)
    return round(time.time() - float(p.read_text()), 1) if p.exists() else None


# ── fechamento do requisito (zero IA) ─────────────────────────────────────────
def close_requirement_manual(req, entries, revisions, summary):
    """Grava o requisito a partir dos itens que o designer já fechou
    manualmente. Nenhuma chamada de API acontece aqui."""
    code = req["code"]
    mods = " and ".join(req["modalities"])

    for layer, key in LAYER_INDEX_KEY.items():
        for item in entries[layer]:
            append_to_index(key, item["label"], code, item["text"])

    def joined(layer):
        return "\n".join(f"{it['label']}: {it['text']}" for it in entries[layer])

    fbs = {
        "code": code, "name_en": req["name_en"], "type": req["type"],
        "modalities": req["modalities"],
        "function": joined("function"),
        "function_summary": entries["function"][0]["label"] if entries["function"] else "",
        "behaviour": joined("behaviour"),
        "behaviour_summary": entries["behaviour"][0]["label"] if entries["behaviour"] else "",
        "structure": joined("structure"),
        "structure_summary": entries["structure"][0]["label"] if entries["structure"] else "",
    }
    (OUT_DIR / f"{code}.json").write_text(json.dumps(fbs, indent=2, ensure_ascii=False))
    (OUT_DIR / f"{code}_log.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    (OUT_DIR / f"{code}_summary.md").write_text(
        f"# {code} — {req['name_en']} ({req['type']})\n\n"
        f"**Modalities:** {mods}\n\n"
        f"## Function\n{fbs['function']}\n\n"
        f"## Behaviour\n{fbs['behaviour']}\n\n"
        f"## Structure\n{fbs['structure']}\n"
    )
    summary[code] = entries["function"][0]["text"][:80] if entries["function"] else ""
    save_summary(summary)

    totals = {
        "calls": 0, "input_tokens": 0, "output_tokens": 0,
        "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 0,
        "elapsed_s": 0, "cost_usd": 0.0,
        "entries_added": sum(len(v) for v in entries.values()),
        "revisions": revisions,
        "wall_clock_s": elapsed_wall_s(code),
    }
    (OUT_DIR / f"{code}_usage.json").write_text(json.dumps(
        {"calls": [], "totals": totals}, indent=2, ensure_ascii=False))
    clear_manual(code)
    _started_path(code).unlink(missing_ok=True)
    return fbs