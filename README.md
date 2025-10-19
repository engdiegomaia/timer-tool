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

#### Opção 1: Usando os scripts prontos

**Linux/Mac:**
```bash
./executar.sh
```

**Windows:**
```
executar.bat
```
Ou simplesmente clique duas vezes no arquivo `executar.bat` no Windows Explorer.

#### Opção 2: Executar diretamente com Python

**Linux/Mac:**
```bash
python3 contador_horas.py
```

**Windows:**
```
python contador_horas.py
```

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

## Estrutura dos Dados

O histórico é salvo em `historico_horas.json` no seguinte formato:

```json
{
    "Nome do Projeto 1": 3600.5,
    "Nome do Projeto 2": 7200.0,
    "Nome do Projeto 3": 1800.25
}
```

Onde os valores representam o total de segundos trabalhados em cada projeto.

## Arquivos do Projeto

- `contador_horas.py`: Código principal da aplicação
- `executar.sh`: Script bash para executar no Linux/Mac
- `executar.bat`: Script batch para executar no Windows
- `requirements.txt`: Documentação das dependências
- `historico_horas.json`: Arquivo gerado automaticamente com o histórico de horas
- `.gitignore`: Arquivos a serem ignorados pelo git
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
- **`parar_contagem()`**: Para o timer e salva no histórico
- **`atualizar_display_tempo()`**: Atualiza o display a cada segundo

## Interface Gráfica

A interface é construída com tkinter e inclui:
- Janela centralizada automaticamente na tela
- Título da aplicação
- Dropdown para seleção de projetos existentes
- Campo de entrada para novos projetos
- Display grande do tempo em execução (formato HH:MM:SS)
- Botões "Iniciar" e "Parar"
- Label mostrando o total acumulado do projeto selecionado

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
- Histórico detalhado com timestamps de início e fim
- Categorização de projetos
- Backup automático do histórico
- Modo escuro/claro

## Licença

Este projeto é de uso livre para fins educacionais e profissionais.

---

**Desenvolvido em**: Outubro de 2025
**Versão**: 1.0

