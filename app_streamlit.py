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
import streamlit as st

if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
if "FBS_OUT_DIR" in st.secrets:
    os.environ["FBS_OUT_DIR"] = st.secrets["FBS_OUT_DIR"]

import anthropic
import fbs_core_ai as core

st.set_page_config(page_title="FBS Design", layout="wide")

INTRO_TEXT = """
### O que você vai fazer

Você vai ajudar a definir elementos de uma interface humano-máquina (HMI) multimodal, num sistema de operações **MUM-T** (Manned-Unmanned Teaming) de **ISR** (Intelligence, Surveillance, Reconnaissance). Cada requisito já vem com contexto suficiente (intenção e modalidades fixas) — você não precisa conhecer os detalhes operacionais completos.

O trabalho é organizado em três camadas, sempre nessa ordem, pra cada requisito:

- **Function (F)** — pra que o artefato serve. Conecta o objetivo de quem projeta ao efeito mensurável do artefato. Function **não** descreve sequência, ordem, lógica de condução ou passos de confirmação — isso é Behaviour.
- **Behaviour (Be)** — o que o artefato **faz**: o fluxo de interação que realiza a função, usando só as modalidades fixas daquele requisito.
- **Structure (S)** — do que o artefato **é feito**: os componentes concretos de HMI e como eles se relacionam.

Uma Function pode dar origem a mais de um Behaviour, e um Behaviour pode reaproveitar Structure já definida em outro lugar — não é uma relação 1:1:1.

### Modalidades fixas

Cada requisito já vem com uma ou mais modalidades definidas. Use só essas — não introduza outras:

- **Touch** — entrada direta numa tela sensível ao toque (tocar, selecionar, arrastar).
- **Keyboard** — teclado físico ou virtual e botões; entrada de texto e valores.
- **Screen** — saída visual; informação renderizada numa tela.
- **Voice-in** — entrada por comando de voz reconhecido (fala transformada em comando).
- **Audio-out** — saída sonora do sistema (alerta acústico ou fala sintetizada).
- **Wearable/HMD** — dispositivo de cabeça (VR/AR/XR). Como entrada: rastreamento de cabeça/olhar, gestos. Como saída: exibição dentro do visor.
- **Haptic** — retorno tátil / força.

### Como isso vai ser avaliado

Isso faz parte de uma pesquisa de doutorado que compara diferentes formas de derivar decisões de projeto de interface a partir de requisitos. Não existe resposta certa ou errada — o que importa é o processo que você segue. Ao final, tem um questionário curto sobre a experiência de usar a ferramenta.
"""

MECHANICS_TEXT = """
### Como funciona aqui

Você vai conversar com o Claude, uma camada de cada vez (Function, depois Behaviour, depois Structure), pra cada um dos {n} requisitos. O Claude propõe, você reage — pode pedir ajustes, discordar, pedir outra opção. Quando estiver satisfeito com uma camada, você fecha ela e segue pra próxima. Não tem tempo limite.
"""

def intro_screen():
    if st.session_state.get("intro_seen"):
        return
    st.title("FBS Design")
    st.markdown(INTRO_TEXT)
    st.markdown(MECHANICS_TEXT.format(n=len(core.REQUIREMENTS)))
    if st.button("Entendi, continuar"):
        st.session_state.intro_seen = True
        st.rerun()
    st.stop()


def designer_gate():
    if "designer_id" in st.session_state:
        return
    st.title("FBS Design")
    st.caption("Identifique-se antes de começar (combine esse código com o pesquisador).")
    designer_input = st.text_input("Seu identificador")
    if st.button("Começar") and designer_input.strip():
        st.session_state.designer_id = core.set_designer(designer_input)
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
    ss.req = core.next_pending_requirement()
    ss.messages = core.load_chat(ss.req["code"]) if ss.req else []


# ── UI ────────────────────────────────────────────────────────────────────────
intro_screen()
designer_gate()
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design")
    st.caption(f"Designer: {st.session_state.designer_id}")
    done = sum(1 for r in core.REQUIREMENTS if core.requirement_done(r["code"]))
    st.progress(done / len(core.REQUIREMENTS),
                text=f"{done}/{len(core.REQUIREMENTS)} requisitos")
    st.divider()
    for r in core.REQUIREMENTS:
        mark = "✅" if core.requirement_done(r["code"]) else (
            "🔵" if ss.req and r["code"] == ss.req["code"] else "⚪")
        st.write(f"{mark} {r['code']} — {r['name_en']}")

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