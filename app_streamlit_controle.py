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
import streamlit as st

if "FBS_OUT_DIR" in st.secrets:
    os.environ["FBS_OUT_DIR"] = st.secrets["FBS_OUT_DIR"]

import fbs_core_human as core

st.set_page_config(page_title="FBS Design — Controle", layout="wide")

LAYERS = ["function", "behaviour", "structure"]
LAYER_LABEL = {"function": "Function", "behaviour": "Behaviour", "structure": "Structure"}

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

Você vai escrever Function, Behaviour e Structure você mesmo, um item de cada vez: um rótulo (label) e uma descrição. Pode adicionar quantos itens quiser em cada camada, remover e reescrever à vontade antes de avançar. Isso vale pra {n} requisitos. Não tem tempo limite.
"""

def render_intro():
    st.markdown(INTRO_TEXT)
    st.markdown(MECHANICS_TEXT.format(n=len(core.REQUIREMENTS)))

def intro_screen():
    if st.session_state.get("intro_seen"):
        return
    st.title("FBS Design — Controle")
    render_intro()
    st.caption("Você pode reabrir esta página a qualquer momento pelo botão ℹ️ na barra lateral.")
    if st.button("Entendi, continuar"):
        st.session_state.intro_seen = True
        st.rerun()
    st.stop()


def designer_gate():
    if "designer_id" in st.session_state:
        return
    st.title("FBS Design — Controle")
    st.caption("Identifique-se antes de começar (combine esse código com o pesquisador).")
    designer_input = st.text_input("Seu identificador")
    if st.button("Começar") and designer_input.strip():
        st.session_state.designer_id = core.set_designer(designer_input)
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
init_state()
ss = st.session_state

with st.sidebar:
    st.title("FBS Design — Controle")
    st.caption(f"Designer: {st.session_state.designer_id}")
    if st.button("ℹ️ Rever instruções", use_container_width=True):
        st.session_state.show_intro = True
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

st.subheader(f"{req['code']} — {req['name_en']} ({req['type']})")
st.caption(f"Modalidades: {mods} · camada atual: {LAYER_LABEL[layer]}")
st.info(f"Intent: {req['intent']}")

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