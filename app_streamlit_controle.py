#!/usr/bin/env python3
"""
FBS Design — interface gráfica (Streamlit), condição controle (zero IA).
O designer entra com Function -> Behaviour -> Structure como itens
estruturados (label + texto), um de cada vez, validando cada um antes
de avançar de camada. Nenhuma chamada a modelo de linguagem acontece em
nenhum momento — nem pra sugerir, nem pra extrair/indexar depois.

Setup:
    pip install streamlit

Usage:
    streamlit run app_streamlit_controle.py
"""

import os
import io
import json
import zipfile
from pathlib import Path
import streamlit as st

if "FBS_OUT_DIR" in st.secrets:
    os.environ["FBS_OUT_DIR"] = st.secrets["FBS_OUT_DIR"]

import fbs_core_human as core

st.set_page_config(page_title="FBS Design — Controle", layout="wide")

LAYERS = ["function", "behaviour", "structure"]
LAYER_LABEL = {"function": "Function", "behaviour": "Behaviour", "structure": "Structure"}
LAYER_HINTS = json.loads(Path("layer_hints.json").read_text())

INTRO_TEXT = Path("intro_text.md").read_text()
MUMT_TEXT = Path("mumt_text.md").read_text()
EXAMPLE_TEXT = Path("example_text.md").read_text()
MECHANICS_TEXT = Path("mechanics_human.md").read_text()
CONDITION = "human"
DESIGNER_FIELDS = [f for f in json.loads(Path("designer_fields.json").read_text())
                   if f.get("only_for", CONDITION) == CONDITION]

def render_intro():
    st.markdown(INTRO_TEXT)
    st.markdown(MECHANICS_TEXT.format(n=len(core.REQUIREMENTS)))

def render_mumt():
    st.markdown(MUMT_TEXT)

def render_example():
    st.markdown(EXAMPLE_TEXT)

@st.dialog("Tela ampliada", width="large")
def _screen_popup(path, caption):
    if caption:
        st.caption(caption)
    st.image(str(path), use_container_width=True)

def render_screens():
    screens = json.loads(Path("screens.json").read_text())
    if not screens:
        st.info("Nenhuma tela cadastrada ainda.")
        return
    for row_start in range(0, len(screens), 2):
        row = screens[row_start:row_start + 2]
        cols = st.columns(2)
        for col, s in zip(cols, row):
            with col:
                path = Path("screens") / s["file"]
                if path.exists():
                    st.image(str(path), caption=s.get("caption", ""), use_container_width=True)
                    if st.button("🔍 Ampliar", key=f"zoom_{s['file']}", use_container_width=True):
                        _screen_popup(path, s.get("caption", ""))
                else:
                    st.warning(f"Imagem não encontrada: screens/{s['file']}")

def intro_screen():
    if st.session_state.get("intro_seen"):
        return
    if st.session_state.get("show_mumt"):
        st.title("Cenário MUM-T")
        render_mumt()
        if st.button("← Voltar"):
            st.session_state.show_mumt = False
            st.rerun()
        st.stop()
    if st.session_state.get("show_example"):
        st.title("Exemplo preenchido")
        render_example()
        if st.button("← Voltar"):
            st.session_state.show_example = False
            st.rerun()
        st.stop()
    st.title("FBS Design — Controle")
    render_intro()
    col1, col2, col3 = st.columns(3)
    if col1.button("💡 Ver um exemplo", use_container_width=True):
        st.session_state.show_example = True
        st.rerun()
    if col2.button("🛩️ Sobre o cenário MUM-T", use_container_width=True):
        st.session_state.show_mumt = True
        st.rerun()
    if col3.button("Entendi, continuar", type="primary", use_container_width=True):
        st.session_state.intro_seen = True
        st.rerun()
    st.caption("Você pode reabrir estas páginas a qualquer momento pela barra lateral.")
    st.stop()


def render_designer_field(f):
    if f["type"] == "text":
        return st.text_input(f["label"])
    if f["type"] == "number":
        return st.number_input(f["label"], min_value=f.get("min", 0), max_value=f.get("max", 100), step=f.get("step", 1))
    if f["type"] == "select":
        return st.selectbox(f["label"], f["options"])
    raise ValueError(f"tipo de campo desconhecido em designer_fields.json: {f['type']}")

def admin_panel():
    st.title("Admin — fbs_human_out")

    req_codes = {r["code"] for r in core.REQUIREMENTS}
    designers = sorted(p.name for p in core.BASE_OUT_DIR.iterdir() if p.is_dir())
    if not designers:
        st.info("Nenhum designer registrado ainda.")
        st.stop()

    for d in designers:
        folder = core.BASE_OUT_DIR / d
        closed = sum(1 for f in folder.glob("*.json") if f.stem in req_codes)
        sus = "✅ respondeu SUS" if (folder / "sus.json").exists() else "— sem SUS ainda"
        em_andamento = "🔵 tem requisito em aberto" if list(folder.glob("*_manual.json")) else ""
        st.write(f"**{d}** — {closed}/{len(core.REQUIREMENTS)} requisitos fechados · {sus} {em_andamento}")

    st.divider()
    st.subheader("Toy problem — pendentes de aprovação")
    pending = []
    for d in designers:
        folder = core.BASE_OUT_DIR / d
        status_path = folder / "toy_status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text())
            if status.get("submitted") and not status.get("approved"):
                pending.append((d, folder))
    if not pending:
        st.caption("Nenhum pendente.")
    for d, folder in pending:
        with st.expander(f"📋 {d}"):
            sub_path = folder / "toy_submission.json"
            if sub_path.exists():
                entries = json.loads(sub_path.read_text())
                for layer in ("function", "behaviour", "structure"):
                    st.markdown(f"**{layer.capitalize()}**")
                    for item in entries.get(layer, []):
                        st.write(f"- {item['label']}: {item['text']}")
            if st.button(f"✅ Aprovar {d}", key=f"approve_{d}"):
                core.approve_toy(folder)
                st.rerun()

    st.divider()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in core.BASE_OUT_DIR.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(core.BASE_OUT_DIR.parent))
    st.download_button("⬇️ Baixar tudo (zip)", data=buf.getvalue(),
                        file_name=f"{core.BASE_OUT_DIR.name}.zip", mime="application/zip")
    st.stop()

if st.query_params.get("admin") == "300":
    admin_panel()


def toy_gate():
    ss = st.session_state
    status = core.toy_status()
    if status.get("approved"):
        return

    if "toy_entries" not in ss:
        ss.toy_entries = {"function": [], "behaviour": [], "structure": []}
        ss.toy_layer_i = 0
        saved = core.load_toy_submission()
        if saved:
            ss.toy_entries = saved
            ss.toy_layer_i = 3

    st.title("Aquecimento — problema de prática")
    st.markdown("##### Antes dos requisitos reais, resolve esse problema simples. "
                "Sem nenhuma ajuda de IA.")

    if status.get("submitted"):
        st.warning("Você já enviou sua resposta. Aguardando aprovação do "
                   "pesquisador pra liberar os requisitos reais.")
        if st.button("🔄 Verificar de novo"):
            st.rerun()
        st.stop()

    try:
        toy_req = core.load_toy_requirement()
    except FileNotFoundError:
        st.error("toy_requirement.json não encontrado — peça pro pesquisador configurar.")
        st.stop()

    layer = LAYERS[ss.toy_layer_i]
    st.success(f"### {toy_req['name_en']}\nIntent: {toy_req['intent']}")

    st.progress(ss.toy_layer_i / 3, text=" → ".join(
        f"**{LAYER_LABEL[l]}**" if l == layer else LAYER_LABEL[l] for l in LAYERS))

    for prev in LAYERS[:ss.toy_layer_i]:
        with st.expander(f"{LAYER_LABEL[prev]} definidas ({len(ss.toy_entries[prev])})", expanded=True):
            for item in ss.toy_entries[prev]:
                st.markdown(f"**{item['label']}** — {item['text']}")

    for i, item in enumerate(ss.toy_entries[layer]):
        col1, col2 = st.columns([9, 1])
        col1.markdown(f"**{item['label']}** — {item['text']}")
        if col2.button("🗑", key=f"toy_del_{layer}_{i}"):
            ss.toy_entries[layer].pop(i)
            st.rerun()

    st.divider()
    st.markdown(f"##### 👉 {LAYER_HINTS[layer]}")
    n = len(ss.toy_entries[layer])
    key_letter = {"function": "F", "behaviour": "Be", "structure": "S"}[layer]
    suggested = f"{key_letter}-TOY.{n + 1}"
    label = st.text_input("Label", value=suggested, key=f"toy_label_{layer}_{n}")
    text = st.text_area(f"Descreva este {LAYER_LABEL[layer]}", key=f"toy_text_{layer}_{n}")

    col1, col2 = st.columns(2)
    if col1.button(f"+ Adicionar {LAYER_LABEL[layer]}", use_container_width=True):
        if text.strip():
            ss.toy_entries[layer].append({"label": label, "text": text.strip()})
            st.rerun()
        else:
            st.warning("Escreva o conteúdo antes de adicionar.")

    can_advance = len(ss.toy_entries[layer]) > 0
    if ss.toy_layer_i < 2:
        if col2.button(f"✔ Fechar {LAYER_LABEL[layer]} e avançar", type="primary",
                       use_container_width=True, disabled=not can_advance):
            ss.toy_layer_i += 1
            st.rerun()
    else:
        if col2.button("✔ Enviar pra aprovação", type="primary",
                       use_container_width=True, disabled=not can_advance):
            core.submit_toy_problem(ss.toy_entries)
            st.rerun()
    st.stop()


def designer_gate():
    if "designer_id" in st.session_state:
        return
    st.title("FBS Design — Controle")
    st.caption("Identifique-se antes de começar (combine esse código com o pesquisador).")
    designer_input = st.text_input("Seu identificador", key="designer_input")
    if not designer_input.strip():
        st.stop()

    if core.designer_registered(designer_input):
        st.session_state.designer_id = core.set_designer(designer_input)
        st.rerun()

    st.info("Esse identificador ainda não foi usado. Preencha os dados abaixo pra registrar.")
    with st.form("registro_form"):
        values = {f["key"]: render_designer_field(f) for f in DESIGNER_FIELDS}
        registrar = st.form_submit_button("Registrar e continuar")
    if registrar:
        missing = [f["label"] for f in DESIGNER_FIELDS
                   if f.get("required", True) and f["type"] == "text" and not values[f["key"]].strip()]
        if missing:
            st.warning(f"Preencha: {', '.join(missing)}")
        else:
            safe = core.set_designer(designer_input)
            core.save_designer_info(values)
            st.session_state.designer_id = safe
            st.rerun()
    st.stop()

def init_state():
    ss = st.session_state
    if "summary" not in ss:
        ss.summary = core.load_summary()
    if "req" not in ss:
        ss.req = core.next_pending_requirement()
        ss.entries = {"function": [], "behaviour": [], "structure": []}
        ss.revisions = {"function": 0, "behaviour": 0, "structure": 0}
        ss.layer_i = 0
        if ss.req:
            core.mark_started(ss.req["code"])
            saved = core.load_manual(ss.req["code"])
            if saved:
                ss.entries = saved["entries"]
                ss.revisions = saved["revisions"]
                ss.layer_i = saved["layer_i"]

def persist():
    ss = st.session_state
    core.save_manual(ss.req["code"], {
        "entries": ss.entries, "revisions": ss.revisions, "layer_i": ss.layer_i,
    })

def suggested_label(layer):
    ss = st.session_state
    r = ss.req["code"][1:]
    key = core.LAYER_INDEX_KEY[layer]
    n = len(ss.entries[layer]) + 1
    return f"{key}-{r}.{n}"

def add_entry(layer, label, text):
    ss = st.session_state
    ss.entries[layer].append({"label": label, "text": text})
    persist()

def remove_entry(layer, idx):
    ss = st.session_state
    ss.entries[layer].pop(idx)
    ss.revisions[layer] += 1
    persist()

def advance_layer():
    ss = st.session_state
    ss.layer_i += 1
    persist()

def do_close_requirement():
    ss = st.session_state
    core.close_requirement_manual(ss.req, ss.entries, ss.revisions, ss.summary)
    st.toast(f"✓ {ss.req['code']} salvo")
    ss.req = core.next_pending_requirement()
    ss.entries = {"function": [], "behaviour": [], "structure": []}
    ss.revisions = {"function": 0, "behaviour": 0, "structure": 0}
    ss.layer_i = 0
    if ss.req:
        core.mark_started(ss.req["code"])


# ── UI ────────────────────────────────────────────────────────────────────────
intro_screen()
designer_gate()
toy_gate()
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design — Controle")
    st.caption(f"Designer: {st.session_state.designer_id}")
    if st.button("ℹ️ Rever instruções", use_container_width=True):
        st.session_state.show_intro = True
        st.rerun()
    if st.button("🛩️ Cenário MUM-T", use_container_width=True):
        st.session_state.show_mumt = True
        st.rerun()
    if st.button("💡 Ver um exemplo", use_container_width=True):
        st.session_state.show_example = True
        st.rerun()
    if st.button("🖥️ Telas existentes", use_container_width=True):
        st.session_state.show_screens = True
        st.rerun()
    done = sum(1 for r in core.REQUIREMENTS if core.requirement_done(r["code"]))
    st.progress(done / len(core.REQUIREMENTS),
                text=f"{done}/{len(core.REQUIREMENTS)} requisitos")
    st.divider()
    for r in core.REQUIREMENTS:
        mark = "✅" if core.requirement_done(r["code"]) else (
            "🔵" if ss.req and r["code"] == ss.req["code"] else "⚪")
        st.write(f"{mark} {r['code']} — {r['name_en']}")

if st.session_state.get("show_intro"):
    render_intro()
    if st.button("← Voltar"):
        st.session_state.show_intro = False
        st.rerun()
    st.stop()

if st.session_state.get("show_mumt"):
    render_mumt()
    if st.button("← Voltar"):
        st.session_state.show_mumt = False
        st.rerun()
    st.stop()

if st.session_state.get("show_example"):
    render_example()
    if st.button("← Voltar"):
        st.session_state.show_example = False
        st.rerun()
    st.stop()

if st.session_state.get("show_screens"):
    render_screens()
    if st.button("← Voltar"):
        st.session_state.show_screens = False
        st.rerun()
    st.stop()

if ss.req is None:
    if not core.sus_done():
        st.subheader("Quase lá — um questionário rápido")
        st.caption("Sobre a ferramenta que você acabou de usar (não sobre o sistema sendo desenhado).")
        st.caption("Escala: 1 = discordo totalmente · 5 = concordo totalmente")
        with st.form("sus_form"):
            responses = [
                st.radio(f"{i + 1}. {text}", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"sus_{i}")
                for i, (text, _) in enumerate(core.SUS_ITEMS)
            ]
            submitted = st.form_submit_button("Enviar")
        if submitted:
            if any(r is None for r in responses):
                st.warning("Responda todos os itens antes de enviar.")
            else:
                core.save_sus(responses)
                st.rerun()
    else:
        st.success(f"Todos os requisitos fechados e questionário respondido. Artefatos em {core.OUT_DIR}/.")
    st.stop()

req = ss.req
layer = LAYERS[ss.layer_i]
mods = ", ".join(req["modalities"])

st.success(f"### {req['code']} — {req['name_en']} ({req['type']})\nModalidades: {mods}  \nIntent: {req['intent']}")

st.progress(ss.layer_i / 3, text=" → ".join(
    f"**{LAYER_LABEL[l]}**" if l == layer else LAYER_LABEL[l] for l in LAYERS))

for prev in LAYERS[:ss.layer_i]:
    with st.expander(f"{LAYER_LABEL[prev]} definidas ({len(ss.entries[prev])})", expanded=True):
        for item in ss.entries[prev]:
            st.markdown(f"**{item['label']}** — {item['text']}")

for i, item in enumerate(ss.entries[layer]):
    col1, col2 = st.columns([9, 1])
    col1.markdown(f"**{item['label']}** — {item['text']}")
    if col2.button("🗑", key=f"del_{layer}_{i}"):
        remove_entry(layer, i)
        st.rerun()

st.divider()
st.markdown(f"##### 👉 {LAYER_HINTS[layer]}")
n = len(ss.entries[layer])
label = st.text_input("Label", value=suggested_label(layer), key=f"label_{layer}_{n}")
text = st.text_area(f"Descreva este {LAYER_LABEL[layer]}", key=f"text_{layer}_{n}")

col1, col2 = st.columns(2)
if col1.button(f"+ Adicionar {LAYER_LABEL[layer]}", use_container_width=True):
    if text.strip():
        add_entry(layer, label, text.strip())
        st.rerun()
    else:
        st.warning("Escreva o conteúdo antes de adicionar.")

can_advance = len(ss.entries[layer]) > 0
if ss.layer_i < 2:
    if col2.button(f"✔ Fechar {LAYER_LABEL[layer]} e avançar", type="primary",
                   use_container_width=True, disabled=not can_advance):
        advance_layer()
        st.rerun()
else:
    if col2.button("✔ Fechar requisito", type="primary",
                   use_container_width=True, disabled=not can_advance):
        do_close_requirement()
        st.rerun()