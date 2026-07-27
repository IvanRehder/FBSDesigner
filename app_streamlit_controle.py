#!/usr/bin/env python3
"""
FBS Design — interface gráfica (Streamlit), condição controle (sem IA).
O designer escreve Function -> Behaviour -> Structure por conta própria,
nesta mesma "conversa" (cada mensagem é dele). O Claude só entra no final,
via core.close_requirement, para extrair/indexar o que já foi decidido —
não participa da criação do conteúdo. Usa fbs_core_human.py.

Setup:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY=sk-...

Usage:
    streamlit run app_streamlit_controle.py
"""

import os
import anthropic
import streamlit as st
import fbs_core_human as core

if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

st.set_page_config(page_title="FBS Design — Controle", layout="wide")


def control_brief(req):
    r = req["code"][1:]
    mods = " and ".join(req["modalities"])
    return (
        f"Requirement {req['code']} ({req['type']}): {req['name_en']}. "
        f"Fixed modalities: {mods}. Intent: {req['intent']}.\n\n"
        "Design this requirement yourself in three layers: Function, Behaviour, "
        "then Structure. Write your notes below as you go — you can revise a "
        "layer before moving to the next.\n"
        f"- Functions: label F-{r}.1, F-{r}.2, ...\n"
        f"- Behaviours: label Be-{r}.<F>.1, ... using your closed F index.\n"
        f"- Structures: label S-{r}.<F>.<Be>.1, ... using your closed F and Be indices."
    )

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

def open_requirement_if_needed():
    ss = st.session_state
    if not ss.messages:
        core.mark_started(ss.req["code"])
        ss.messages.append({"role": "user", "content": control_brief(ss.req)})
        core.save_chat(ss.req["code"], ss.messages)

def do_close_requirement():
    ss = st.session_state
    with st.spinner("Fechando requisito, extraindo F/Be/S e atualizando índice..."):
        fbs, warnings = core.close_requirement(
            ss.client, ss.req, ss.messages, ss.summary)
    ss.warnings = warnings
    if fbs is None:
        return  # não avança — mostra os warnings e deixa tentar de novo
    st.toast(f"✓ {ss.req['code']} salvo")
    ss.req = core.next_pending_requirement()
    ss.messages = core.load_chat(ss.req["code"]) if ss.req else []


# ── UI ────────────────────────────────────────────────────────────────────────
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design — Controle")
    done = sum(1 for r in core.REQUIREMENTS if core.requirement_done(r["code"]))
    st.progress(done / len(core.REQUIREMENTS),
                text=f"{done}/{len(core.REQUIREMENTS)} requisitos")
    st.divider()
    for r in core.REQUIREMENTS:
        mark = "✅" if core.requirement_done(r["code"]) else (
            "🔵" if ss.req and r["code"] == ss.req["code"] else "⚪")
        st.write(f"{mark} {r['code']} — {r['name_en']}")

if ss.req is None:
    st.success("Todos os requisitos fechados. Artefatos em fbs_out/.")
    st.stop()

req = ss.req
st.subheader(f"{req['code']} — {req['name_en']} ({req['type']})")
st.caption(f"Modalidades: {', '.join(req['modalities'])} · "
           "você conduz Function → Behaviour → Structure sozinho, sem sugestões")

for w in ss.warnings:
    st.warning(f"{w}")

open_requirement_if_needed()

for m in ss.messages[1:]:  # esconde o brief inicial
    with st.chat_message("user"):
        st.markdown(m["content"])

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("✔ Fechar requisito", type="primary", use_container_width=True):
        do_close_requirement()
        st.rerun()

user_msg = st.chat_input("Escreva sua proposta ou revisão...")
if user_msg:
    ss.messages.append({"role": "user", "content": user_msg})
    core.save_chat(ss.req["code"], ss.messages)
    st.rerun()