#!/usr/bin/env python3
"""
FBS Design — interface gráfica (Streamlit) para o designer.
Uma conversa por requisito; o modelo conduz F -> Be -> S sozinho.
Mesma lógica do CLI (fbs_core.py); os dois leem/escrevem fbs_out/.

Setup:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY=sk-...

Usage:
    streamlit run app_streamlit.py
"""

import os
import io
import json
import zipfile
from pathlib import Path
import streamlit as st
import anthropic
from core import fbs_core_ai as core

st.set_page_config(page_title="FBS Design", layout="wide")

CONTENT_DIR = Path("content")

LAYERS = ["function", "behaviour", "structure"]
LAYER_LABEL = {"function": "Function", "behaviour": "Behaviour", "structure": "Structure"}
LAYER_HINTS = json.loads((CONTENT_DIR / "layer_hints.json").read_text(encoding="utf-8"))
CONDITION_PREFIX = "ai"
PARTICIPANT_DIGITS = 2  # ajusta aqui se os números dos participantes tiverem outra quantidade de dígitos

INTRO_TEXT = (CONTENT_DIR / "intro_text.md").read_text(encoding="utf-8")
MUMT_TEXT = (CONTENT_DIR / "mumt_text.md").read_text(encoding="utf-8")
EXAMPLE_TEXT = (CONTENT_DIR / "example_text.md").read_text(encoding="utf-8")
MECHANICS_TEXT = (CONTENT_DIR / "mechanics_ai.md").read_text(encoding="utf-8")
CONDITION = "ai"
DESIGNER_FIELDS = [f for f in json.loads((CONTENT_DIR / "designer_fields.json").read_text(encoding="utf-8"))
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
    screens = json.loads((CONTENT_DIR / "screens.json").read_text(encoding="utf-8"))
    if not screens:
        st.info("Nenhuma tela cadastrada ainda.")
        return
    for row_start in range(0, len(screens), 2):
        row = screens[row_start:row_start + 2]
        cols = st.columns(2)
        for col, s in zip(cols, row):
            with col:
                path = CONTENT_DIR / "screens" / s["file"]
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
    st.title("FBS Design")
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
    st.title(f"Admin — {core.BASE_OUT_DIR}")

    req_codes = {r["code"] for r in core.REQUIREMENTS}
    designers = sorted(p.name for p in core.BASE_OUT_DIR.iterdir() if p.is_dir())
    if not designers:
        st.info("Nenhum designer registrado ainda.")
        st.stop()

    for d in designers:
        folder = core.BASE_OUT_DIR / d
        closed = sum(1 for f in folder.glob("*.json") if f.stem in req_codes)
        sus = "✅ respondeu SUS" if (folder / "sus.json").exists() else "— sem SUS ainda"
        em_andamento = "🔵 tem requisito em aberto" if list(folder.glob("*_chat.json")) else ""
        st.write(f"**{d}** — {closed}/{len(core.REQUIREMENTS)} requisitos fechados · {sus} {em_andamento}")

    st.divider()
    st.subheader("Toy problem — enviados (informativo, não bloqueia ninguém)")
    enviados = []
    for d in designers:
        folder = core.BASE_OUT_DIR / d
        status_path = folder / "toy_status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if status.get("submitted"):
                enviados.append((d, folder))
    if not enviados:
        st.caption("Nenhum ainda.")
    for d, folder in enviados:
        with st.expander(f"📋 {d}"):
            sub_path = folder / "toy_submission.json"
            if sub_path.exists():
                entries = json.loads(sub_path.read_text(encoding="utf-8"))
                for layer in ("function", "behaviour", "structure"):
                    st.markdown(f"**{layer.capitalize()}**")
                    for item in entries.get(layer, []):
                        st.write(f"- {item['label']}: {item['text']}")

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
    if status.get("acknowledged"):
        return

    if "toy_entries" not in ss:
        ss.toy_entries = {"function": [], "behaviour": [], "structure": []}
        ss.toy_layer_i = 0
        saved = core.load_toy_submission()
        if saved:
            ss.toy_entries = saved

    st.title("Aquecimento — problema de prática")
    st.markdown("##### Antes dos requisitos reais, resolve esse problema simples. "
                "Sem nenhuma ajuda de IA, mesmo aqui na condição com IA.")

    if status.get("submitted"):
        st.success("Você terminou o problema de prática.")
        st.write(
            "Se tiver alguma dúvida sobre como isso funciona, fala com o "
            "pesquisador antes de continuar. Se estiver tudo certo, é só "
            "seguir em frente pros requisitos reais."
        )
        col1, col2 = st.columns(2)
        if col1.button("✏️ Quero revisar minha resposta", use_container_width=True):
            core.reopen_toy()
            st.rerun()
        if col2.button("Continuar", type="primary", use_container_width=True):
            core.acknowledge_toy()
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
    st.title("FBS Design")
    st.caption(f"Digite seu número de participante ({PARTICIPANT_DIGITS} dígitos, combinado com o pesquisador).")
    numero_input = st.text_input("Número do participante", key="designer_input", max_chars=PARTICIPANT_DIGITS)
    raw = numero_input.strip()
    if not raw:
        st.stop()
    if not raw.isdigit() or len(raw) > PARTICIPANT_DIGITS:
        st.warning(f"Digite só números, até {PARTICIPANT_DIGITS} dígitos.")
        st.stop()
    designer_input = f"{CONDITION_PREFIX}_{raw.zfill(PARTICIPANT_DIGITS)}"

    if core.designer_registered(designer_input):
        st.session_state.designer_id = core.set_designer(designer_input)
        st.rerun()

    st.info("Esse número ainda não foi usado. Preencha os dados abaixo pra registrar.")
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
    if "client" not in ss:
        ss.client = anthropic.Anthropic()
    if "summary" not in ss:
        ss.summary = core.load_summary()
    if "req" not in ss:
        ss.req = core.next_pending_requirement()
        ss.messages = []
        ss.warnings = []
        if ss.req:
            ss.messages = core.load_chat(ss.req["code"])

def ask_claude():
    ss = st.session_state
    system = core.fbs_system(ss.summary)
    with st.spinner("Claude pensando..."):
        reply = core.chat_turn(ss.client, system, ss.messages)
    ss.messages.append({"role": "assistant", "content": reply})
    core.save_chat(ss.req["code"], ss.messages)

def open_requirement_if_needed():
    ss = st.session_state
    if not ss.messages:
        core.mark_started(ss.req["code"])
        ss.messages.append({"role": "user", "content": core.opening_prompt(ss.req)})
        ask_claude()

def do_close_requirement():
    ss = st.session_state
    with st.spinner("Fechando requisito, extraindo F/Be/S e atualizando índice..."):
        fbs, warnings = core.close_requirement(
            ss.client, ss.req, ss.messages, ss.summary)
    ss.warnings = warnings
    if fbs is None:
        return  # não avança — mostra os warnings e deixa tentar de novo
    st.toast(f"✓ {ss.req['code']} salvo")
    if ss.get("revising_code"):
        ss.revision_notice = core.downstream_affected(ss.revising_code, ss.revising_old_closed_at)
        ss.revising_code = None
        ss.revising_old_closed_at = None
    ss.req = core.next_pending_requirement()
    ss.messages = core.load_chat(ss.req["code"]) if ss.req else []

def start_revision(code):
    ss = st.session_state
    old_closed_at, _ = core.reopen_requirement(code)
    ss.revising_code = code
    ss.revising_old_closed_at = old_closed_at
    ss.req = next(r for r in core.REQUIREMENTS if r["code"] == code)
    ss.messages = []
    ss.warnings = []


# ── UI ────────────────────────────────────────────────────────────────────────
intro_screen()
designer_gate()
toy_gate()
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design")
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

    done_codes = [r["code"] for r in core.REQUIREMENTS if core.requirement_done(r["code"])]
    if done_codes:
        st.divider()
        st.caption("Revisar um requisito já fechado")
        pick = st.selectbox("Requisito", done_codes, label_visibility="collapsed", key="revise_pick")
        if st.button("✏️ Revisar", use_container_width=True):
            start_revision(pick)
            st.rerun()

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

if ss.get("revision_notice") is not None:
    affected = ss.revision_notice
    if affected:
        st.warning(
            "Estes requisitos já tinham sido fechados usando a versão anterior "
            f"deste como referência: **{', '.join(affected)}**. Pode valer a pena "
            "reconferir se ainda fazem sentido juntos."
        )
    else:
        st.success("Nenhum requisito posterior foi afetado por essa revisão.")
    if st.button("OK, entendi"):
        ss.revision_notice = None
        st.rerun()

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
        st.success(f"Todos os requisitos fechados e questionário respondido. Artefatos em {core.current_out_dir()}/.")
    st.stop()

req = ss.req
st.subheader(f"{req['code']} — {req['name_en']} ({req['type']})")
st.caption(f"Modalidades: {', '.join(req['modalities'])} · "
           "o Claude conduz Function → Behaviour → Structure nesta mesma conversa")

for w in ss.warnings:
    st.warning(f"{w}")

open_requirement_if_needed()

for m in ss.messages[1:]:  # esconde o opening_prompt
    with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
        st.markdown(m["content"])

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("✔ Fechar requisito", type="primary", use_container_width=True):
        do_close_requirement()
        st.rerun()

user_msg = st.chat_input("Responda ao Claude (discussão livre)...")
if user_msg:
    ss.messages.append({"role": "user", "content": user_msg})
    ask_claude()
    st.rerun()