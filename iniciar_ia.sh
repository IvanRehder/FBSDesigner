#!/usr/bin/env bash

# Dá dois cliques nesse arquivo (Mac) ou roda "bash iniciar_ia.sh" (Linux)
# num terminal aberto nesta pasta. Não precisa saber Python pra usar isso —
# só precisa ter Python instalado na máquina.

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

# Verifica se existe uma chave válida
API_KEY=""

if [ -f ".env" ]; then
    API_KEY=$(grep '^ANTHROPIC_API_KEY=' .env 2>/dev/null | head -n 1 | cut -d '=' -f2-)
fi

# Se não existir ou estiver vazia, pergunta
if [ -z "$API_KEY" ]; then
    echo ""
    echo "Preciso da sua chave de API da Anthropic (o pesquisador te passa isso)."

    IFS= read -r -p "Cola a chave aqui e aperta Enter: " API_KEY

    if [ -z "$API_KEY" ]; then
        echo ""
        echo "Nenhuma chave foi informada."
        read -r -p "Aperta Enter pra fechar..."
        exit 1
    fi

    # Remove qualquer linha antiga/vazia da chave,
    # preservando as outras configurações do .env
    if [ -f ".env" ]; then
        grep -v '^ANTHROPIC_API_KEY=' .env > .env.tmp || true
        mv .env.tmp .env
    fi

    # Grava a chave corretamente
    printf '%s\n' "ANTHROPIC_API_KEY=$API_KEY" >> .env
fi

if [ "$DEBUG" -eq 1 ]; then
    echo "CHAVE DA API OK"
    read -r -p "Aperta Enter pra continuar..."
fi

echo ""
echo "Abrindo o app no navegador..."

streamlit run app_streamlit.py --browser.gatherUsageStats=false