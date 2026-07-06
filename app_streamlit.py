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
import anthropic
import streamlit as st
import fbs_core as core

if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

st.set_page_config(page_title="FBS Design", layout="wide")


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
    ss.req = core.next_pending_requirement()
    ss.messages = core.load_chat(ss.req["code"]) if ss.req else []


# ── UI ────────────────────────────────────────────────────────────────────────
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design")
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
