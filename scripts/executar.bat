@echo off
REM Script para executar o Timer Tool no Windows

REM Define o diretório do script
cd /d "%~dp0\.."

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Erro: Python nao esta instalado.
    echo Por favor, instale o Python antes de executar este programa.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verifica se o tkinter está disponível
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Erro: Tkinter nao esta disponivel.
    echo O tkinter geralmente vem com Python no Windows.
    echo Reinstale o Python e certifique-se de marcar "tcl/tk and IDLE" durante a instalacao.
    pause
    exit /b 1
)

REM Executa o programa
echo Iniciando Timer Tool...
python -m horas_trabalhadas.contador_horas

REM Verifica se houve erro
if errorlevel 1 (
    echo.
    echo O programa terminou com erro.
    pause
    exit /b 1
)

exit /b 0

