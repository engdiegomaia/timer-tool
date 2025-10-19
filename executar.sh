#!/bin/bash
# Script para executar o Timer Tool no Linux/Mac

# Define o diretório do script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Muda para o diretório do script
cd "$DIR"

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não está instalado."
    echo "Por favor, instale o Python 3 antes de executar este programa."
    exit 1
fi

# Verifica se o tkinter está disponível
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Erro: Tkinter não está instalado."
    echo "Para instalar no Ubuntu/Debian, execute:"
    echo "sudo apt-get install python3-tk"
    exit 1
fi

# Executa o programa
echo "Iniciando Timer Tool..."
python3 contador_horas.py

# Captura o código de saída
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "O programa terminou com erro (código: $EXIT_CODE)"
    read -p "Pressione Enter para fechar..."
fi

exit $EXIT_CODE

