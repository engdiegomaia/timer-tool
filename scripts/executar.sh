#!/bin/bash
# Script para executar o Timer Tool no Linux/Mac

# Define o diretório do script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Muda para o diretório raiz do projeto
cd "$DIR/.."

# Adiciona o diretório src ao PYTHONPATH
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não está instalado."
    echo "Por favor, instale o Python 3 antes de executar este programa."
    read -p "Pressione Enter para fechar..."
    exit 1
fi

# Verifica se o tkinter está disponível
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Erro: Tkinter não está instalado."
    echo "Para instalar no Ubuntu/Debian, execute:"
    echo "sudo apt-get install python3-tk"
    read -p "Pressione Enter para fechar..."
    exit 1
fi

# Executa o programa em background sem manter o terminal
python3 -m horas_trabalhadas.contador_horas &

# Fecha o terminal imediatamente
exit 0

