#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timer Tool
Sistema simples para rastrear horas trabalhadas em diferentes projetos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import time


class ContadorHoras:
    """Classe principal para o contador de horas trabalhadas."""
    
    def __init__(self, root):
        """
        Inicializa o contador de horas.
        
        Args:
            root: Janela principal do tkinter
        """
        self.root = root
        self.root.title("Timer Tool")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        
        # Centraliza a janela na tela
        self.centralizar_janela()
        
        # Arquivo para persistência dos dados
        # Determina o diretório de dados de forma robusta
        # Tenta encontrar o diretório raiz do projeto
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        # Sobe até encontrar o diretório com setup.py ou pyproject.toml
        base_dir = current_dir
        for _ in range(4):  # Máximo 4 níveis acima
            if os.path.exists(os.path.join(base_dir, "setup.py")) or \
               os.path.exists(os.path.join(base_dir, "pyproject.toml")):
                break
            parent = os.path.dirname(base_dir)
            if parent == base_dir:  # Chegou na raiz
                # Se não encontrou, usa o diretório do usuário
                base_dir = os.path.expanduser("~")
                break
            base_dir = parent
        
        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        self.arquivo_historico = os.path.join(data_dir, "historico_horas.json")
        
        # Variáveis de controle
        self.tempo_inicio = None  # Timestamp do início da contagem
        self.tempo_decorrido = 0  # Tempo decorrido em segundos
        self.contando = False  # Flag indicando se está contando
        self.timer_id = None  # ID do timer para poder cancelá-lo
        
        # Carregar histórico de projetos e horas
        self.historico = self.carregar_historico()
        
        # Criar interface gráfica
        self.criar_interface()
        
        # Atualizar lista de projetos no dropdown
        self.atualizar_dropdown_projetos()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        # Atualiza a janela para obter as dimensões corretas
        self.root.update_idletasks()
        
        # Obtém as dimensões da janela
        largura_janela = self.root.winfo_width()
        altura_janela = self.root.winfo_height()
        
        # Obtém as dimensões da tela
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        
        # Calcula a posição central
        posicao_x = (largura_tela // 2) - (largura_janela // 2)
        posicao_y = (altura_tela // 2) - (altura_janela // 2)
        
        # Define a geometria com a posição central
        self.root.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
    
    def carregar_historico(self):
        """
        Carrega o histórico de horas trabalhadas do arquivo JSON.
        
        Returns:
            dict: Dicionário com projetos e suas horas trabalhadas
        """
        if os.path.exists(self.arquivo_historico):
            try:
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
                    # Migrar formato antigo para novo (se necessário)
                    return self.migrar_formato_historico(historico)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}")
                return {}
        return {}
    
    def migrar_formato_historico(self, historico):
        """
        Migra o formato antigo do histórico (apenas segundos) para o novo formato (com sessões e datas).
        
        Args:
            historico: Dicionário do histórico carregado
            
        Returns:
            dict: Histórico no novo formato
        """
        novo_historico = {}
        for projeto, dados in historico.items():
            # Se já está no novo formato
            if isinstance(dados, dict) and 'sessoes' in dados:
                novo_historico[projeto] = dados
            # Se está no formato antigo (apenas número)
            elif isinstance(dados, (int, float)):
                novo_historico[projeto] = {
                    'total_segundos': dados,
                    'sessoes': []
                }
        return novo_historico
    
    def salvar_historico(self):
        """Salva o histórico de horas trabalhadas no arquivo JSON."""
        try:
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(self.historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar histórico: {e}")
    
    def criar_interface(self):
        """Cria todos os elementos da interface gráfica."""
        # Configura o grid da janela principal para centralizar
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0)
        
        # Título
        titulo = ttk.Label(main_frame, text="Timer Tool", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Seção de seleção de projeto
        ttk.Label(main_frame, text="Selecionar Projeto Existente:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, 
                                                   pady=(0, 5))
        
        # Dropdown de projetos
        self.projeto_var = tk.StringVar()
        self.dropdown_projetos = ttk.Combobox(main_frame, textvariable=self.projeto_var, 
                                              state="readonly", width=40)
        self.dropdown_projetos.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").grid(row=3, column=0, 
                                                             columnspan=2, 
                                                             sticky=(tk.W, tk.E), 
                                                             pady=10)
        
        # Seção de novo projeto
        ttk.Label(main_frame, text="Ou Criar Novo Projeto:", 
                 font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, 
                                                   pady=(0, 5))
        
        # Campo de texto para novo projeto
        self.novo_projeto_var = tk.StringVar()
        self.entrada_novo_projeto = ttk.Entry(main_frame, 
                                              textvariable=self.novo_projeto_var, 
                                              width=42)
        self.entrada_novo_projeto.grid(row=5, column=0, columnspan=2, pady=(0, 15))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").grid(row=6, column=0, 
                                                             columnspan=2, 
                                                             sticky=(tk.W, tk.E), 
                                                             pady=10)
        
        # Display do tempo
        self.label_tempo = ttk.Label(main_frame, text="00:00:00", 
                                     font=("Arial", 24, "bold"), 
                                     foreground="blue")
        self.label_tempo.grid(row=7, column=0, columnspan=2, pady=15)
        
        # Frame para os botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Botão Iniciar
        self.btn_iniciar = ttk.Button(botoes_frame, text="Iniciar", 
                                      command=self.iniciar_contagem, 
                                      width=15)
        self.btn_iniciar.grid(row=0, column=0, padx=5)
        
        # Botão Parar
        self.btn_parar = ttk.Button(botoes_frame, text="Parar", 
                                    command=self.parar_contagem, 
                                    width=15, state="disabled")
        self.btn_parar.grid(row=0, column=1, padx=5)
        
        # Label para exibir total de horas do projeto selecionado
        self.label_total = ttk.Label(main_frame, text="", 
                                     font=("Arial", 10), 
                                     foreground="green")
        self.label_total.grid(row=9, column=0, columnspan=2, pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").grid(row=10, column=0, 
                                                             columnspan=2, 
                                                             sticky=(tk.W, tk.E), 
                                                             pady=10)
        
        # Frame para botões de relatórios
        relatorios_frame = ttk.Frame(main_frame)
        relatorios_frame.grid(row=11, column=0, columnspan=2, pady=10)
        
        ttk.Label(relatorios_frame, text="Relatórios:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # Botão Log Semanal
        self.btn_log_semanal = ttk.Button(relatorios_frame, text="Log Semanal", 
                                          command=self.gerar_log_semanal, 
                                          width=15)
        self.btn_log_semanal.grid(row=1, column=0, padx=5)
        
        # Botão Log Mensal
        self.btn_log_mensal = ttk.Button(relatorios_frame, text="Log Mensal", 
                                         command=self.gerar_log_mensal, 
                                         width=15)
        self.btn_log_mensal.grid(row=1, column=1, padx=5)
        
        # Bind para atualizar total quando projeto é selecionado
        self.dropdown_projetos.bind("<<ComboboxSelected>>", self.atualizar_total_projeto)
    
    def atualizar_dropdown_projetos(self):
        """Atualiza a lista de projetos no dropdown."""
        projetos = sorted(self.historico.keys())
        self.dropdown_projetos['values'] = projetos
        if projetos:
            self.dropdown_projetos.current(0)
            self.atualizar_total_projeto()
    
    def atualizar_total_projeto(self, event=None):
        """Atualiza o display do total de horas do projeto selecionado."""
        projeto = self.projeto_var.get()
        if projeto and projeto in self.historico:
            total_segundos = self.historico[projeto]['total_segundos']
            horas, resto = divmod(total_segundos, 3600)
            minutos, segundos = divmod(resto, 60)
            self.label_total.config(
                text=f"Total acumulado no projeto: {int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"
            )
        else:
            self.label_total.config(text="")
    
    def obter_projeto_selecionado(self):
        """
        Obtém o projeto selecionado ou o novo projeto digitado.
        
        Returns:
            str: Nome do projeto ou None se nenhum foi selecionado/digitado
        """
        novo_projeto = self.novo_projeto_var.get().strip()
        projeto_existente = self.projeto_var.get().strip()
        
        # Prioriza o novo projeto se foi digitado algo
        if novo_projeto:
            return novo_projeto
        elif projeto_existente:
            return projeto_existente
        else:
            return None
    
    def iniciar_contagem(self):
        """Inicia a contagem de tempo."""
        projeto = self.obter_projeto_selecionado()
        
        if not projeto:
            messagebox.showwarning("Aviso", 
                                 "Selecione um projeto existente ou digite um novo projeto!")
            return
        
        # Inicia a contagem
        self.tempo_inicio = time.time()
        self.tempo_decorrido = 0
        self.contando = True
        
        # Desabilita controles
        self.btn_iniciar.config(state="disabled")
        self.dropdown_projetos.config(state="disabled")
        self.entrada_novo_projeto.config(state="disabled")
        
        # Habilita botão parar
        self.btn_parar.config(state="normal")
        
        # Inicia o timer
        self.atualizar_display_tempo()
        
        messagebox.showinfo("Iniciado", f"Contagem iniciada para o projeto: {projeto}")
    
    def parar_contagem(self):
        """Para a contagem de tempo e salva no histórico."""
        if not self.contando:
            return
        
        projeto = self.obter_projeto_selecionado()
        
        # Para a contagem
        self.contando = False
        tempo_final = time.time()
        tempo_trabalhado = tempo_final - self.tempo_inicio
        
        # Cancela o timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Registra a data e hora de início da sessão
        data_hora_inicio = datetime.fromtimestamp(self.tempo_inicio)
        
        # Atualiza o histórico com a nova estrutura
        if projeto in self.historico:
            self.historico[projeto]['total_segundos'] += tempo_trabalhado
            self.historico[projeto]['sessoes'].append({
                'data': data_hora_inicio.isoformat(),
                'duracao_segundos': tempo_trabalhado
            })
        else:
            self.historico[projeto] = {
                'total_segundos': tempo_trabalhado,
                'sessoes': [{
                    'data': data_hora_inicio.isoformat(),
                    'duracao_segundos': tempo_trabalhado
                }]
            }
        
        # Salva o histórico
        self.salvar_historico()
        
        # Formata o tempo trabalhado para exibição
        horas, resto = divmod(int(tempo_trabalhado), 3600)
        minutos, segundos = divmod(resto, 60)
        
        # Reabilita controles
        self.btn_iniciar.config(state="normal")
        self.dropdown_projetos.config(state="readonly")
        self.entrada_novo_projeto.config(state="normal")
        self.btn_parar.config(state="disabled")
        
        # Limpa o campo de novo projeto
        self.novo_projeto_var.set("")
        
        # Atualiza o dropdown de projetos
        self.atualizar_dropdown_projetos()
        
        # Reseta o display
        self.label_tempo.config(text="00:00:00")
        
        messagebox.showinfo("Parado", 
                          f"Tempo registrado para '{projeto}':\n"
                          f"{horas:02d}:{minutos:02d}:{segundos:02d}")
    
    def atualizar_display_tempo(self):
        """Atualiza o display do tempo decorrido."""
        if self.contando:
            # Calcula tempo decorrido
            tempo_atual = time.time()
            self.tempo_decorrido = tempo_atual - self.tempo_inicio
            
            # Formata o tempo
            horas, resto = divmod(int(self.tempo_decorrido), 3600)
            minutos, segundos = divmod(resto, 60)
            
            # Atualiza o display
            self.label_tempo.config(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
            
            # Agenda próxima atualização (a cada 1 segundo)
            self.timer_id = self.root.after(1000, self.atualizar_display_tempo)
    
    def filtrar_sessoes_por_periodo(self, data_inicio, data_fim):
        """
        Filtra as sessões de todos os projetos dentro de um período.
        
        Args:
            data_inicio: Data de início do período (datetime)
            data_fim: Data de fim do período (datetime)
            
        Returns:
            dict: Dicionário com projetos e suas sessões no período
        """
        sessoes_periodo = {}
        
        for projeto, dados in self.historico.items():
            sessoes_filtradas = []
            
            for sessao in dados['sessoes']:
                data_sessao = datetime.fromisoformat(sessao['data'])
                
                if data_inicio <= data_sessao <= data_fim:
                    sessoes_filtradas.append(sessao)
            
            if sessoes_filtradas:
                total_segundos = sum(s['duracao_segundos'] for s in sessoes_filtradas)
                sessoes_periodo[projeto] = {
                    'sessoes': sessoes_filtradas,
                    'total_segundos': total_segundos
                }
        
        return sessoes_periodo
    
    def formatar_duracao(self, segundos):
        """
        Formata a duração em segundos para HH:MM:SS.
        
        Args:
            segundos: Duração em segundos
            
        Returns:
            str: Duração formatada
        """
        horas, resto = divmod(int(segundos), 3600)
        minutos, segundos_rest = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos_rest:02d}"
    
    def gerar_log_semanal(self):
        """Gera e exibe o log de horas da última semana."""
        # Calcula o período da última semana
        hoje = datetime.now()
        data_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
        data_inicio = (hoje - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.exibir_log(data_inicio, data_fim, "Semanal")
    
    def gerar_log_mensal(self):
        """Gera e exibe o log de horas do último mês."""
        # Calcula o período do último mês
        hoje = datetime.now()
        data_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
        data_inicio = (hoje - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.exibir_log(data_inicio, data_fim, "Mensal")
    
    def centralizar_janela_log(self, janela_log):
        """Centraliza a janela de log na tela."""
        janela_log.update_idletasks()
        largura_janela = janela_log.winfo_width()
        altura_janela = janela_log.winfo_height()
        largura_tela = janela_log.winfo_screenwidth()
        altura_tela = janela_log.winfo_screenheight()
        posicao_x = (largura_tela // 2) - (largura_janela // 2)
        posicao_y = (altura_tela // 2) - (altura_janela // 2)
        janela_log.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")
    
    def exibir_log(self, data_inicio, data_fim, tipo_log):
        """
        Exibe o log de horas em uma janela separada.
        
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            tipo_log: Tipo do log (Semanal ou Mensal)
        """
        # Filtra sessões do período
        sessoes_periodo = self.filtrar_sessoes_por_periodo(data_inicio, data_fim)
        
        if not sessoes_periodo:
            messagebox.showinfo("Log " + tipo_log, 
                              f"Nenhuma sessão encontrada no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
            return
        
        # Cria janela para o log
        janela_log = tk.Toplevel(self.root)
        janela_log.title(f"Log {tipo_log} - {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        janela_log.geometry("700x500")
        
        # Configura grid para centralizar
        janela_log.grid_rowconfigure(0, weight=1)
        janela_log.grid_columnconfigure(0, weight=1)
        
        # Frame principal com scrollbar
        frame_principal = ttk.Frame(janela_log, padding="10")
        frame_principal.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        
        # Criar Canvas com Scrollbar
        canvas = tk.Canvas(frame_principal)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        frame_scrollavel = ttk.Frame(canvas)
        
        def atualizar_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        frame_scrollavel.bind("<Configure>", atualizar_scrollregion)
        
        canvas_window = canvas.create_window(0, 0, window=frame_scrollavel, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def atualizar_largura_canvas(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", atualizar_largura_canvas)
        
        canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configura o grid do frame principal
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        
        # Frame para centralizar conteúdo horizontalmente
        frame_central = ttk.Frame(frame_scrollavel)
        frame_central.pack(expand=True, fill=tk.BOTH, pady=20)
        
        # Container para centralizar o conteúdo interno horizontalmente
        # Usa expand=True sem fill para centralizar horizontalmente
        frame_conteudo = ttk.Frame(frame_central)
        frame_conteudo.pack(expand=True)
        
        # Título (centralizado)
        titulo = tk.Label(frame_conteudo, 
                          text=f"Relatório {tipo_log}", 
                          font=("Arial", 14, "bold"),
                          justify="center")
        titulo.pack(pady=(0, 10))
        
        # Período (centralizado)
        periodo = tk.Label(frame_conteudo, 
                           text=f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
                           font=("Arial", 10),
                           justify="center")
        periodo.pack(pady=(0, 20))
        
        # Total geral (centralizado)
        total_geral_segundos = sum(dados['total_segundos'] for dados in sessoes_periodo.values())
        total_geral = tk.Label(frame_conteudo,
                               text=f"Total Geral: {self.formatar_duracao(total_geral_segundos)}",
                               font=("Arial", 12, "bold"),
                               fg="green",
                               justify="center")
        total_geral.pack(pady=(0, 20))
        
        # Exibe cada projeto
        for projeto, dados in sorted(sessoes_periodo.items()):
            # Frame para o projeto (centralizado com padding horizontal)
            frame_projeto = ttk.LabelFrame(frame_conteudo, text=projeto, padding="10")
            frame_projeto.pack(fill=tk.X, padx=50, pady=5)
            
            # Frame interno para centralizar tudo no projeto
            frame_interno = ttk.Frame(frame_projeto)
            frame_interno.pack(expand=True)
            frame_interno.grid_columnconfigure(0, weight=1)
            
            # Total do projeto (centralizado)
            total_projeto = tk.Label(frame_interno,
                                     text=f"Total: {self.formatar_duracao(dados['total_segundos'])}",
                                     font=("Arial", 10, "bold"),
                                     justify="center")
            total_projeto.grid(row=0, column=0, pady=(0, 5))
            
            # Lista de sessões (centralizada)
            for i, sessao in enumerate(sorted(dados['sessoes'], key=lambda x: x['data']), 1):
                data_sessao = datetime.fromisoformat(sessao['data'])
                duracao = self.formatar_duracao(sessao['duracao_segundos'])
                
                texto_sessao = f"{i}. {data_sessao.strftime('%d/%m/%Y %H:%M')} - Duração: {duracao}"
                label_sessao = tk.Label(frame_interno, text=texto_sessao, justify="center")
                label_sessao.grid(row=i, column=0, pady=2)
        
        # Botão para fechar (centralizado)
        btn_fechar = ttk.Button(frame_conteudo, text="Fechar", 
                               command=janela_log.destroy)
        btn_fechar.pack(pady=20)
        
        # Centraliza a janela na tela
        self.centralizar_janela_log(janela_log)


def main():
    """Função principal para iniciar a aplicação."""
    root = tk.Tk()
    app = ContadorHoras(root)
    root.mainloop()


if __name__ == "__main__":
    main()

