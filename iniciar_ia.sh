#!/usr/bin/env bash
# Dá dois cliques nesse arquivo (Mac) ou roda "bash iniciar_ia.sh" (Linux)
# num terminal aberto nesta pasta. Não precisa saber Python pra usar isso —
# só precisa ter Python instalado na máquina.

set -e
cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado nesta máquina."
    echo "Instala em https://www.python.org/downloads/ e roda este arquivo de novo."
    read -p "Aperta Enter pra fechar..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Primeira vez rodando — preparando o ambiente (só demora dessa vez)..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Verifica se existe uma chave válida
API_KEY=""

if [ -f ".env" ]; then
    API_KEY=$(grep '^ANTHROPIC_API_KEY=' .env 2>/dev/null | head -n 1 | cut -d '=' -f2-)
fi

# Se não existir ou estiver vazia, pergunta
if [ -z "$API_KEY" ]; then
    echo ""
    echo "Preciso da sua chave de API da Anthropic (o pesquisador te passa isso)."
    read -p "Cola a chave aqui e aperta Enter: " API_KEY

    if [ -z "$API_KEY" ]; then
        echo ""
        echo "Nenhuma chave foi informada."
        read -p "Aperta Enter pra fechar..."
        exit 1
    fi

    # Remove uma eventual linha antiga/vazia
    if [ -f ".env" ]; then
        grep -v '^ANTHROPIC_API_KEY=' .env > .env.tmp || true
        mv .env.tmp .env
    fi

    # Grava a chave correta
    echo "ANTHROPIC_API_KEY=$API_KEY" >> .env
fi

echo ""
echo "Abrindo o app no navegador..."
streamlit run app_streamlit.py --browser.gatherUsageStats=false