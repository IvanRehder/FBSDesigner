@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

REM ============================================================
REM MODO DEBUG
REM Rode com:
REM iniciar.bat --debug
REM ============================================================

set DEBUG=0
if "%1"=="--debug" set DEBUG=1

if %DEBUG%==1 (
    echo PASTA ATUAL: %cd%
    pause
)

REM ============================================================
REM VERIFICA PYTHON
REM ============================================================

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

REM ============================================================
REM CRIA O VENV SE NECESSARIO
REM ============================================================

if not exist venv (
    echo Primeira vez rodando -- preparando o ambiente ^(so demora dessa vez^)...
    python -m venv venv
)

if %DEBUG%==1 (
    echo VENV OK OU JA EXISTIA
    dir venv\Scripts\activate.bat
    pause
)

REM ============================================================
REM ATIVA O VENV
REM ============================================================

call venv\Scripts\activate.bat

if %DEBUG%==1 (
    echo ATIVOU O VENV
    pause
)

REM ============================================================
REM INSTALA / ATUALIZA DEPENDENCIAS
REM Normal: silencioso
REM Debug: mostra a saida completa do pip
REM ============================================================

set QUIET=-q

if %DEBUG%==1 set QUIET=

pip install %QUIET% -r requirements.txt

if %DEBUG%==1 (
    echo PACOTES INSTALADOS
    pause
)

REM ============================================================
REM VERIFICA A CHAVE DA ANTHROPIC
REM
REM Nao basta existir ANTHROPIC_API_KEY no .env:
REM ela precisa ter um valor.
REM ============================================================

set "API_KEY="

if exist .env (
    for /f "tokens=1,* delims==" %%A in ('findstr /B "ANTHROPIC_API_KEY=" .env') do (
        set "API_KEY=%%B"
    )
)

REM ============================================================
REM SE NAO EXISTIR UMA CHAVE VALIDA, PEDE AO USUARIO
REM ============================================================

if not defined API_KEY (
    echo.
    echo Preciso da sua chave de API da Anthropic ^(o pesquisador te passa isso^).

    set /p "API_KEY=Cola a chave aqui e aperta Enter: "

    if not defined API_KEY (
        echo.
        echo Nenhuma chave foi informada.
        pause
        exit /b 1
    )

    REM Recria o .env com a chave correta.
    REM Delayed Expansion evita problemas com varios caracteres
    REM especiais presentes na chave.
    > .env echo ANTHROPIC_API_KEY=!API_KEY!
)

if %DEBUG%==1 (
    echo CHAVE DA API OK
    echo.
    pause
)

REM ============================================================
REM ABRE O APP
REM ============================================================

echo.
echo Abrindo o app no navegador...

streamlit run app_streamlit.py --browser.gatherUsageStats=false

pause