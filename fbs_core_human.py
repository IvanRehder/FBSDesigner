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

BASE_OUT_DIR = Path(os.environ.get("FBS_OUT_DIR", "fbs_human_out"))
OUT_DIR = BASE_OUT_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)

def set_designer(designer_id):
    """Redireciona OUT_DIR pra uma subpasta por designer. Chamar uma vez,
    antes de qualquer outra função que leia/grave em OUT_DIR."""
    global OUT_DIR
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in designer_id.strip().lower())
    OUT_DIR = BASE_OUT_DIR / safe
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return safe

REQUIREMENTS = json.loads(Path("requirements.json").read_text())
LAYER_INDEX_KEY = {"function": "F", "behaviour": "Be", "structure": "S"}

def load_summary():
    p = OUT_DIR / "_summary.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}

def save_summary(summary):
    (OUT_DIR / "_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

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
    return (OUT_DIR / "sus.json").exists()

def save_sus(responses):
    score = sus_score(responses)
    (OUT_DIR / "sus.json").write_text(json.dumps(
        {"responses": responses, "score": score}, indent=2, ensure_ascii=False))
    return score


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