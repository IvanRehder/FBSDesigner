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
import streamlit as st
from pathlib import Path

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
    (current_out_dir() / "designer_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

REQUIREMENTS = json.loads(Path("requirements.json").read_text(encoding="utf-8"))
LAYER_INDEX_KEY = {"function": "F", "behaviour": "Be", "structure": "S"}

def load_summary():
    p = current_out_dir() / "_summary.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def save_summary(summary):
    (current_out_dir() / "_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

def append_to_index(layer, label, code, text):
    idx_path = current_out_dir() / "elements_index.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {"F": [], "Be": [], "S": []}
    idx[layer].append({"label": label, "requirement": code, "text": text})
    idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")

def save_manual(code, state):
    (current_out_dir() / f"{code}_manual.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def load_manual(code):
    p = current_out_dir() / f"{code}_manual.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def clear_manual(code):
    p = current_out_dir() / f"{code}_manual.json"
    if p.exists():
        p.unlink()

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
        {"responses": responses, "score": score}, indent=2, ensure_ascii=False), encoding="utf-8")
    return score


# ── toy problem (aquecimento, sempre zero IA, precisa de aprovação) ──────────
def load_toy_requirement():
    return json.loads(Path("toy_requirement.json").read_text(encoding="utf-8"))

def toy_status():
    p = current_out_dir() / "toy_status.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"submitted": False, "approved": False}

def load_toy_submission():
    p = current_out_dir() / "toy_submission.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def submit_toy_problem(entries):
    (current_out_dir() / "toy_submission.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    (current_out_dir() / "toy_status.json").write_text(json.dumps(
        {"submitted": True, "approved": False}, indent=2, ensure_ascii=False), encoding="utf-8")

def approve_toy(designer_folder):
    """Usado pelo painel admin, que opera fora do designer 'atual' — por
    isso recebe a pasta explicitamente em vez de depender de current_out_dir()."""
    p = designer_folder / "toy_status.json"
    status = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"submitted": True, "approved": False}
    status["approved"] = True
    p.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")

def reopen_toy():
    """Usado pelo próprio designer, na tela de 'aguardando aprovação', pra
    poder editar e reenviar em vez de ficar travado esperando."""
    status = toy_status()
    status["submitted"] = False
    (current_out_dir() / "toy_status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")


# ── cronometragem de parede ───────────────────────────────────────────────────
def _started_path(code):
    return current_out_dir() / f"{code}_started.txt"

def mark_started(code):
    p = _started_path(code)
    if not p.exists():
        p.write_text(str(time.time()), encoding="utf-8")

def elapsed_wall_s(code):
    p = _started_path(code)
    return round(time.time() - float(p.read_text(encoding="utf-8")), 1) if p.exists() else None


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
        "closed_at": time.time(),
        "function": joined("function"),
        "function_summary": entries["function"][0]["label"] if entries["function"] else "",
        "behaviour": joined("behaviour"),
        "behaviour_summary": entries["behaviour"][0]["label"] if entries["behaviour"] else "",
        "structure": joined("structure"),
        "structure_summary": entries["structure"][0]["label"] if entries["structure"] else "",
    }
    (current_out_dir() / f"{code}.json").write_text(json.dumps(fbs, indent=2, ensure_ascii=False), encoding="utf-8")
    (current_out_dir() / f"{code}_log.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    (current_out_dir() / f"{code}_summary.md").write_text(
        f"# {code} — {req['name_en']} ({req['type']})\n\n"
        f"**Modalities:** {mods}\n\n"
        f"## Function\n{fbs['function']}\n\n"
        f"## Behaviour\n{fbs['behaviour']}\n\n"
        f"## Structure\n{fbs['structure']}\n", encoding="utf-8")
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
    (current_out_dir() / f"{code}_usage.json").write_text(json.dumps(
        {"calls": [], "totals": totals}, indent=2, ensure_ascii=False), encoding="utf-8")
    clear_manual(code)
    _started_path(code).unlink(missing_ok=True)
    return fbs


# ── revisão de requisito já fechado ───────────────────────────────────────────
def reopen_requirement(code):
    """Designer decidiu revisar um requisito já fechado. Arquiva o
    fechamento antigo (não perde o dado) e libera o código pra ser refeito.
    Retorna (closed_at antigo, conteúdo antigo de {code}_log.json — as
    entradas F/Be/S de antes, prontas pra recarregar na edição)."""
    p = current_out_dir() / f"{code}.json"
    old = json.loads(p.read_text(encoding="utf-8"))
    old_closed_at = old.get("closed_at")
    old_log_path = current_out_dir() / f"{code}_log.json"
    old_log = json.loads(old_log_path.read_text(encoding="utf-8")) if old_log_path.exists() else None
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
    """Requisitos já fechados depois de `code` (podem ter sido feitos
    olhando pra versão antiga dele, se o designer usa isso como referência
    mental — não existe dependência automática nessa condição, mas ainda
    vale avisar)."""
    if old_closed_at is None:
        return []
    affected = []
    for req in REQUIREMENTS:
        other = req["code"]
        if other == code:
            continue
        p = current_out_dir() / f"{other}.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("closed_at", 0) > old_closed_at:
                affected.append(other)
    return affected
