@echo off
cd /d "%~dp0"

set DEBUG=0
if "%1"=="--debug" set DEBUG=1

if %DEBUG%==1 echo PASTA ATUAL: %cd%
if %DEBUG%==1 pause

where python >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado nesta maquina.
    echo Instala em https://www.python.org/downloads/ e roda este arquivo de novo.
    echo IMPORTANTE: na instalacao, marca a opcao "Add Python to PATH".
    pause
    exit /b 1
)
if %DEBUG%==1 echo PYTHON OK
if %DEBUG%==1 pause

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
if %DEBUG%==1 echo ATIVOU O VENV
if %DEBUG%==1 pause

set QUIET=-q
if %DEBUG%==1 set QUIET=
pip install %QUIET% -r requirements.txt
if %DEBUG%==1 echo PACOTES INSTALADOS
if %DEBUG%==1 pause

if not exist .env (
    type nul > .env
)
findstr /C:"ANTHROPIC_API_KEY" .env >nul 2>&1
if errorlevel 1 (
    echo.
    echo Preciso da sua chave de API da Anthropic ^(o pesquisador te passa isso^).
    set /p API_KEY="Cola a chave aqui e aperta Enter: "
    echo ANTHROPIC_API_KEY=%API_KEY%>> .env
)

echo.
echo Abrindo o app no navegador...
streamlit run app_streamlit.py
pause