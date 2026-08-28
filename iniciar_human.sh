#!/usr/bin/env bash

# Dá dois cliques nesse arquivo (Mac) ou roda "bash iniciar_human.sh" (Linux)
# num terminal aberto nesta pasta. Não precisa saber Python pra usar isso —
# só precisa ter Python instalado na máquina. Essa condição não usa IA,
# então não pede chave de API nenhuma.

set -e
cd "$(dirname "$0")"

DEBUG=0
if [ "${1:-}" = "--debug" ]; then
    DEBUG=1
fi

if [ "$DEBUG" -eq 1 ]; then
    echo "PASTA ATUAL: $(pwd)"
    read -r -p "Aperta Enter pra continuar..."
fi

if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado nesta máquina."
    echo "Instala em https://www.python.org/downloads/ e roda este arquivo de novo."
    read -r -p "Aperta Enter pra fechar..."
    exit 1
fi

if [ "$DEBUG" -eq 1 ]; then
    echo "PYTHON OK"
    read -r -p "Aperta Enter pra continuar..."
fi

if [ ! -d "venv" ]; then
    echo "Primeira vez rodando — preparando o ambiente (só demora dessa vez)..."
    python3 -m venv venv
fi

if [ "$DEBUG" -eq 1 ]; then
    echo "VENV OK OU JÁ EXISTIA"
    ls -l venv/bin/activate
    read -r -p "Aperta Enter pra continuar..."
fi

source venv/bin/activate

if [ "$DEBUG" -eq 1 ]; then
    echo "ATIVOU O VENV"
    read -r -p "Aperta Enter pra continuar..."
fi

if [ "$DEBUG" -eq 1 ]; then
    pip install -r requirements.txt
else
    pip install -q -r requirements.txt
fi

if [ "$DEBUG" -eq 1 ]; then
    echo "PACOTES INSTALADOS"
    read -r -p "Aperta Enter pra continuar..."
fi

echo ""
echo "Abrindo o app no navegador..."

streamlit run app_streamlit_human.py --browser.gatherUsageStats=false