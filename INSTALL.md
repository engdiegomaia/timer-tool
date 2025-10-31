# Guia de Instalação - Horas Trabalhadas

## Pré-requisitos

- Python 3.7 ou superior
- Tkinter (geralmente incluído com Python)

### Instalação do Tkinter (Linux)

Se o tkinter não estiver instalado:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## Instalação

### Opção 1: Instalação via pip (Recomendado)

```bash
# Instalar do diretório local
pip install .

# Ou instalar em modo desenvolvimento
pip install -e .
```

Após a instalação, você pode executar com:
```bash
horas-trabalhadas
```

### Opção 2: Usando Make (Linux/Mac)

```bash
# Instalar
make install

# Ou instalar em modo desenvolvimento
make install-dev

# Executar
make run
```

### Opção 3: Execução direta sem instalação

#### Linux/Mac:
```bash
chmod +x scripts/executar.sh
./scripts/executar.sh
```

#### Windows:
```cmd
scripts\executar.bat
```

### Opção 4: Execução direta via Python

```bash
# A partir da raiz do projeto
python -m horas_trabalhadas.contador_horas
```

## Desenvolvimento

Para desenvolver e fazer alterações no código:

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Ou usando Make
make install-dev
```

Isso permite editar o código e ver as mudanças imediatamente sem reinstalar.

## Build e Distribuição

Para criar pacotes distribuíveis:

```bash
# Usando Make
make build

# Ou manualmente
python setup.py sdist bdist_wheel
```

Os arquivos serão criados em `dist/`.

## Limpeza

Para remover arquivos temporários e builds:

```bash
make clean
```

## Estrutura de Diretórios

```
horas-trabalhadas/
├── src/
│   └── horas_trabalhadas/
│       ├── __init__.py
│       └── contador_horas.py
├── scripts/
│   ├── executar.bat
│   └── executar.sh
├── data/
│   └── historico_horas.json (gerado automaticamente)
├── setup.py
├── pyproject.toml
├── Makefile
├── requirements.txt
└── README.md
```

## Solução de Problemas

### Python não encontrado
Certifique-se de que Python está instalado e no PATH:
```bash
python --version
# ou
python3 --version
```

### Tkinter não disponível
No Windows, reinstale o Python marcando "tcl/tk and IDLE".
No Linux, instale o pacote python3-tk conforme mostrado acima.

### Erro de importação
Se ocorrer erro ao importar o módulo, certifique-se de estar na raiz do projeto ou que o pacote foi instalado corretamente.

