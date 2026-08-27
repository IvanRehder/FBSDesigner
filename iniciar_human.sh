#!/usr/bin/env bash
# Dá dois cliques nesse arquivo (Mac) ou roda "bash iniciar_human.sh" (Linux)
# num terminal aberto nesta pasta. Não precisa saber Python pra usar isso —
# só precisa ter Python instalado na máquina. Essa condição não usa IA,
# então não pede chave de API nenhuma.

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

echo ""
echo "Abrindo o app no navegador..."
streamlit run app_streamlit_human.py --browser.gatherUsageStats=false