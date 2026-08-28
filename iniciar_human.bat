@echo off

REM Da dois cliques neste arquivo. Nao precisa saber Python pra usar isso --
REM so precisa ter Python instalado na maquina. Essa condicao nao usa IA,
REM entao nao pede chave de API nenhuma.

cd /d "%~dp0"

set DEBUG=0
if "%1"=="--debug" set DEBUG=1

if %DEBUG%==1 (
    echo PASTA ATUAL: %cd%
    pause
)

where python >nul 2>&1

if errorlevel 1 (
    echo Python nao encontrado nesta maquina.
    echo Instala em https://www.python.org/downloads/ e roda este arquivo de novo.
    echo IMPORTANTE: na instalacao, marca a opcao "Add Python to PATH".
    pause
    exit /b 1
)

if %DEBUG%==1 (
    echo PYTHON OK
    pause
)

if not exist venv (
    echo Primeira vez rodando -- preparando o ambiente ^(so demora dessa vez^)...
    python -m venv venv
)

if %DEBUG%==1 (
    echo VENV OK OU JA EXISTIA
    dir venv\Scripts\activate.bat
    pause
)

call venv\Scripts\activate.bat

if %DEBUG%==1 (
    echo ATIVOU O VENV
    pause
)

set QUIET=-q
if %DEBUG%==1 set QUIET=

pip install %QUIET% -r requirements.txt

if %DEBUG%==1 (
    echo PACOTES INSTALADOS
    pause
)

echo.
echo Abrindo o app no navegador...

streamlit run app_streamlit_human.py --browser.gatherUsageStats=false

pause