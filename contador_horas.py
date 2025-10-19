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
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Centraliza a janela na tela
        self.centralizar_janela()
        
        # Arquivo para persistência dos dados
        self.arquivo_historico = "historico_horas.json"
        
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
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}")
                return {}
        return {}
    
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
            total_segundos = self.historico[projeto]
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
        
        # Atualiza o histórico
        if projeto in self.historico:
            self.historico[projeto] += tempo_trabalhado
        else:
            self.historico[projeto] = tempo_trabalhado
        
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


def main():
    """Função principal para iniciar a aplicação."""
    root = tk.Tk()
    app = ContadorHoras(root)
    root.mainloop()


if __name__ == "__main__":
    main()

