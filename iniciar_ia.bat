@echo off
REM Da dois cliques neste arquivo. Nao precisa saber Python pra usar isso --
REM so precisa ter Python instalado na maquina.
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

REM Evita a pergunta de e-mail do Streamlit na primeira execucao
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"

if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    > "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
    >> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
)

echo.
echo Abrindo o app no navegador...
streamlit run app_streamlit.py
pause
