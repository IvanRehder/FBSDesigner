@echo off
REM Da dois cliques neste arquivo. Nao precisa saber Python pra usar isso --
REM so precisa ter Python instalado na maquina. Essa condicao nao usa IA,
REM entao nao pede chave de API nenhuma.
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado nesta maquina.
    echo Instala em https://www.python.org/downloads/ e roda este arquivo de novo.
    echo IMPORTANTE: na instalacao, marca a opcao "Add Python to PATH".
    pause
    exit /b 1
)

if not exist venv (
    echo Primeira vez rodando -- preparando o ambiente ^(so demora dessa vez^)...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo Abrindo o app no navegador...
streamlit run app_streamlit_human.py
pause
