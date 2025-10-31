# Timer Tool

Sistema simples em Python para rastrear e registrar horas trabalhadas em diferentes projetos usando interface gráfica.

## Descrição

O Timer Tool é uma aplicação desktop que permite:
- Controlar o tempo trabalhado em diferentes projetos
- Selecionar projetos existentes de um dropdown
- Criar novos projetos dinamicamente
- Visualizar o tempo em execução em tempo real
- Persistir automaticamente o histórico de horas em arquivo JSON
- Visualizar o total acumulado de horas por projeto

## Funcionalidades

1. **Dropdown de Projetos**: Selecione um projeto existente da lista de projetos já trabalhados
2. **Novo Projeto**: Campo de texto para inserir o nome de um novo projeto
3. **Botão Iniciar**: Inicia a contagem de tempo para o projeto selecionado
4. **Botão Parar**: Finaliza a contagem e salva as horas no histórico
5. **Display de Tempo**: Mostra o tempo decorrido no formato HH:MM:SS
6. **Persistência**: Histórico salvo automaticamente em `historico_horas.json`
7. **Carregamento Automático**: O histórico é carregado ao iniciar o programa
8. **Total Acumulado**: Exibe o total de horas já trabalhadas em cada projeto
9. **Registro de Data**: Cada sessão de trabalho registra automaticamente a data e hora de início
10. **Log Semanal**: Gera relatório detalhado das horas trabalhadas nos últimos 7 dias
11. **Log Mensal**: Gera relatório detalhado das horas trabalhadas nos últimos 30 dias

## Requisitos

- Python 3.x
- Tkinter (incluído na instalação padrão do Python)

### Instalação do Tkinter (Linux)

Se o tkinter não estiver instalado no seu sistema Linux:

```bash
sudo apt-get install python3-tk
```

## Como Usar

### Executar a Aplicação

#### Opção 1: Instalação via pip (Recomendado)

```bash
pip install .
```

Após instalar, execute:
```bash
horas-trabalhadas
```

#### Opção 2: Usando os scripts prontos

**Linux/Mac:**
```bash
chmod +x scripts/executar.sh
./scripts/executar.sh
```

**Windows:**
```
scripts\executar.bat
```
Ou simplesmente clique duas vezes no arquivo `scripts\executar.bat` no Windows Explorer.

#### Opção 3: Usando Make (Linux/Mac)

```bash
make install
make run
```

#### Opção 4: Executar diretamente com Python

```bash
# A partir da raiz do projeto
python -m horas_trabalhadas.contador_horas
```

Para mais detalhes, consulte [INSTALL.md](INSTALL.md).

### Fluxo de Uso

1. **Selecionar um Projeto**:
   - Use o dropdown para selecionar um projeto existente, OU
   - Digite o nome de um novo projeto no campo "Criar Novo Projeto"

2. **Iniciar a Contagem**:
   - Clique no botão "Iniciar"
   - O display começará a contar o tempo em segundos
   - Os controles de seleção serão desabilitados durante a contagem

3. **Parar a Contagem**:
   - Clique no botão "Parar"
   - O tempo trabalhado será adicionado ao histórico do projeto
   - O histórico será salvo automaticamente
   - Uma mensagem exibirá o tempo registrado

4. **Visualizar Histórico**:
   - Selecione um projeto no dropdown
   - O total acumulado será exibido abaixo dos botões

5. **Gerar Relatórios**:
   - Clique em "Log Semanal" para ver horas dos últimos 7 dias
   - Clique em "Log Mensal" para ver horas dos últimos 30 dias
   - Os relatórios mostram todas as sessões com data/hora e duração de cada uma

## Estrutura dos Dados

O histórico é salvo em `historico_horas.json` no seguinte formato:

```json
{
    "Nome do Projeto 1": {
        "total_segundos": 3600.5,
        "sessoes": [
            {
                "data": "2025-10-29T14:30:00",
                "duracao_segundos": 3600.5
            }
        ]
    },
    "Nome do Projeto 2": {
        "total_segundos": 7200.0,
        "sessoes": [
            {
                "data": "2025-10-29T10:00:00",
                "duracao_segundos": 7200.0
            }
        ]
    }
}
```

Cada projeto contém:
- **total_segundos**: Total acumulado de segundos trabalhados no projeto
- **sessoes**: Lista de todas as sessões de trabalho com data/hora de início e duração

O sistema realiza migração automática de dados do formato antigo (apenas número) para o novo formato (com sessões e datas).

## Arquivos do Projeto

### Estrutura do Projeto

```
horas-trabalhadas/
├── src/
│   └── horas_trabalhadas/      # Código fonte
│       ├── __init__.py
│       └── contador_horas.py
├── scripts/                    # Scripts de execução
│   ├── executar.sh            # Linux/Mac
│   └── executar.bat           # Windows
├── data/                       # Dados gerados pela aplicação
│   └── historico_horas.json   # (gerado automaticamente)
├── setup.py                    # Script de instalação
├── pyproject.toml             # Configuração do projeto
├── Makefile                    # Comandos de build
├── requirements.txt            # Dependências
├── INSTALL.md                  # Guia de instalação
└── README.md                   # Esta documentação
```

### Arquivos Principais

- `src/horas_trabalhadas/contador_horas.py`: Código principal da aplicação
- `scripts/executar.sh`: Script bash para executar no Linux/Mac
- `scripts/executar.bat`: Script batch para executar no Windows
- `setup.py`: Script de instalação do pacote
- `pyproject.toml`: Configuração moderna do projeto Python
- `Makefile`: Comandos para build, instalação e limpeza
- `requirements.txt`: Documentação das dependências
- `data/historico_horas.json`: Arquivo gerado automaticamente com o histórico de horas
- `.gitignore`: Arquivos a serem ignorados pelo git
- `INSTALL.md`: Guia detalhado de instalação
- `README.md`: Esta documentação

## Estrutura do Código

### Classe Principal: `ContadorHoras`

- **`__init__()`**: Inicializa a aplicação e carrega o histórico
- **`centralizar_janela()`**: Centraliza a janela na tela do usuário
- **`carregar_historico()`**: Carrega dados do arquivo JSON
- **`salvar_historico()`**: Salva dados no arquivo JSON
- **`criar_interface()`**: Cria todos os elementos da interface gráfica
- **`atualizar_dropdown_projetos()`**: Atualiza a lista de projetos no dropdown
- **`atualizar_total_projeto()`**: Exibe o total de horas do projeto selecionado
- **`obter_projeto_selecionado()`**: Retorna o projeto ativo (novo ou existente)
- **`iniciar_contagem()`**: Inicia o timer de contagem
- **`parar_contagem()`**: Para o timer e salva no histórico com data/hora
- **`atualizar_display_tempo()`**: Atualiza o display a cada segundo
- **`migrar_formato_historico()`**: Converte dados do formato antigo para o novo formato
- **`filtrar_sessoes_por_periodo()`**: Filtra sessões dentro de um período específico
- **`gerar_log_semanal()`**: Gera relatório das horas da última semana
- **`gerar_log_mensal()`**: Gera relatório das horas do último mês
- **`exibir_log()`**: Exibe relatório detalhado em janela separada
- **`formatar_duracao()`**: Formata segundos para HH:MM:SS
- **`centralizar_janela_log()`**: Centraliza janela de log na tela

## Interface Gráfica

A interface é construída com tkinter e inclui:
- Janela centralizada automaticamente na tela
- Título da aplicação
- Dropdown para seleção de projetos existentes
- Campo de entrada para novos projetos
- Display grande do tempo em execução (formato HH:MM:SS)
- Botões "Iniciar" e "Parar"
- Label mostrando o total acumulado do projeto selecionado
- Botões "Log Semanal" e "Log Mensal" para gerar relatórios
- Janelas de relatório com conteúdo centralizado e scrollbar

## Características Técnicas

- **Linguagem**: Python 3
- **Interface**: tkinter
- **Persistência**: JSON
- **Atualização**: Timer de 1 segundo para atualização do display
- **Encoding**: UTF-8 para suporte a caracteres especiais

## Melhorias Futuras

Possíveis melhorias para versões futuras:
- Exportar relatórios em CSV ou PDF
- Gráficos de tempo por projeto
- Categorização de projetos
- Backup automático do histórico
- Modo escuro/claro
- Filtros personalizados de data nos relatórios

## Licença

Este projeto é de uso livre para fins educacionais e profissionais.

---

**Desenvolvido em**: Outubro de 2025
**Versão**: 1.1

