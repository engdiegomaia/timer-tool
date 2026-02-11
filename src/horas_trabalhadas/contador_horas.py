#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timer Tool / Ponto
Sistema para rastrear horas trabalhadas e registro de ponto (entrada/saída) em projetos.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ContadorHoras:
    """Classe principal para o contador de horas e registro de ponto."""

    def __init__(self, root):
        self.root = root
        self.root.title("Timer Tool — Ponto e Horas")
        self.root.geometry("520x620")
        self.root.resizable(True, True)
        self.root.minsize(480, 560)

        self.centralizar_janela()
        self._configurar_estilos()

        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        base_dir = current_dir
        for _ in range(4):
            if os.path.exists(os.path.join(base_dir, "setup.py")) or \
               os.path.exists(os.path.join(base_dir, "pyproject.toml")):
                break
            parent = os.path.dirname(base_dir)
            if parent == base_dir:
                base_dir = os.path.expanduser("~")
                break
            base_dir = parent

        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.debug("Diretório data criado: %s", data_dir)
        self.arquivo_historico = os.path.join(data_dir, "historico_horas.json")
        self.arquivo_sessao_aberta = os.path.join(data_dir, "sessao_aberta.json")
        self.intervalo_checkpoint_seg = 60
        logger.debug("Arquivo de histórico: %s", self.arquivo_historico)

        self.tempo_inicio = None
        self.tempo_decorrido = 0
        self.contando = False
        self.timer_id = None
        self.checkpoint_id = None
        self.projeto_em_andamento = None

        self.historico = self.carregar_historico()
        logger.debug("Histórico carregado: %d projeto(s) -> %s", len(self.historico), list(self.historico.keys()))
        self._sessao_recuperada_msg = None
        self.recuperar_sessao_aberta()
        self.criar_interface()
        self.atualizar_dropdown_projetos()
        if getattr(self, "_sessao_recuperada_msg", None):
            self.root.after(100, lambda: messagebox.showinfo("Sessão recuperada", self._sessao_recuperada_msg))

    def _configurar_estilos(self):
        """Aplica estilos visuais à interface."""
        self.style = ttk.Style()
        if self.style.theme_use():
            self.style.theme_use("default")
        self.style.configure("TFrame", background="#f0f4f8")
        self.style.configure("Card.TFrame", background="#ffffff", relief="flat")
        self.style.configure(
            "TLabel",
            background="#f0f4f8",
            font=("Segoe UI", 10),
            foreground="#1a2332",
        )
        self.style.configure(
            "Title.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground="#0d2137",
        )
        self.style.configure(
            "Section.TLabel",
            font=("Segoe UI", 11, "bold"),
            foreground="#2d3748",
        )
        self.style.configure(
            "Timer.TLabel",
            font=("Segoe UI", 28, "bold"),
            foreground="#2563eb",
        )
        self.style.configure(
            "Total.TLabel",
            font=("Segoe UI", 10),
            foreground="#059669",
        )
        self.style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(12, 8),
        )
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
        )
        self.root.configure(background="#f0f4f8")

    def centralizar_janela(self):
        self.root.update_idletasks()
        largura_janela = self.root.winfo_width()
        altura_janela = self.root.winfo_height()
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        posicao_x = (largura_tela // 2) - (largura_janela // 2)
        posicao_y = (altura_tela // 2) - (altura_janela // 2)
        self.root.geometry(f"{max(520, largura_janela)}x{max(620, altura_janela)}+{posicao_x}+{posicao_y}")

    def carregar_historico(self):
        if os.path.exists(self.arquivo_historico):
            logger.debug("Carregando histórico de %s", self.arquivo_historico)
            try:
                with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                    historico = json.load(f)
                    migrado = self.migrar_formato_historico(historico)
                    logger.debug("Histórico migrado: %s", list(migrado.keys()))
                    return migrado
            except Exception as e:
                logger.exception("Erro ao carregar histórico: %s", e)
                messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}")
                return {}
        logger.debug("Arquivo de histórico não existe, iniciando com histórico vazio")
        return {}

    def migrar_formato_historico(self, historico):
        novo_historico = {}
        for projeto, dados in historico.items():
            if isinstance(dados, dict) and "sessoes" in dados:
                novo_historico[projeto] = dados
            elif isinstance(dados, (int, float)):
                novo_historico[projeto] = {
                    "total_segundos": dados,
                    "sessoes": [],
                }
        return novo_historico

    def salvar_sessao_aberta(self):
        """Grava sessão em aberto em arquivo para recuperação em caso de encerramento abrupto."""
        if not self.contando or not self.projeto_em_andamento or self.tempo_inicio is None:
            return
        try:
            agora = time.time()
            dados = {
                "projeto": self.projeto_em_andamento,
                "tempo_inicio": self.tempo_inicio,
                "ultima_atualizacao": agora,
            }
            with open(self.arquivo_sessao_aberta, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2)
            logger.debug("Checkpoint sessão aberta salvo: %s", self.projeto_em_andamento)
        except Exception as e:
            logger.exception("Erro ao salvar sessão aberta: %s", e)

    def agendar_checkpoint(self):
        """Agenda o próximo salvamento periódico da sessão em aberto."""
        if not self.contando:
            return
        self.salvar_sessao_aberta()
        self.checkpoint_id = self.root.after(
            self.intervalo_checkpoint_seg * 1000, self.agendar_checkpoint
        )

    def recuperar_sessao_aberta(self):
        """Se existir sessão aberta de execução anterior, incorpora ao histórico."""
        if not os.path.exists(self.arquivo_sessao_aberta):
            return
        try:
            with open(self.arquivo_sessao_aberta, "r", encoding="utf-8") as f:
                dados = json.load(f)
            projeto = dados.get("projeto")
            tempo_inicio = dados.get("tempo_inicio")
            ultima_atualizacao = dados.get("ultima_atualizacao", tempo_inicio)
            if not projeto or tempo_inicio is None:
                os.remove(self.arquivo_sessao_aberta)
                return
            duracao_seg = ultima_atualizacao - tempo_inicio
            if duracao_seg <= 0:
                os.remove(self.arquivo_sessao_aberta)
                return
            data_inicio = datetime.fromtimestamp(tempo_inicio)
            data_fim = datetime.fromtimestamp(ultima_atualizacao)
            sessao = {
                "data": data_inicio.isoformat(),
                "data_saida": data_fim.isoformat(),
                "duracao_segundos": duracao_seg,
            }
            if projeto in self.historico:
                self.historico[projeto]["total_segundos"] += duracao_seg
                self.historico[projeto]["sessoes"].append(sessao)
            else:
                self.historico[projeto] = {
                    "total_segundos": duracao_seg,
                    "sessoes": [sessao],
                }
            self.salvar_historico()
            os.remove(self.arquivo_sessao_aberta)
            logger.debug("Sessão recuperada: %s duracao=%.1fs", projeto, duracao_seg)
            horas, resto = divmod(int(duracao_seg), 3600)
            minutos, segs = divmod(resto, 60)
            self._sessao_recuperada_msg = (
                f"Sessão interrompida recuperada: '{projeto}' — "
                f"{int(horas):02d}:{int(minutos):02d}:{int(segs):02d} (até o último registro)."
            )
        except Exception as e:
            logger.exception("Erro ao recuperar sessão aberta: %s", e)
            try:
                os.remove(self.arquivo_sessao_aberta)
            except OSError:
                pass

    def salvar_historico(self):
        logger.debug("Salvando histórico em %s (projetos: %s)", self.arquivo_historico, list(self.historico.keys()))
        try:
            with open(self.arquivo_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, indent=4, ensure_ascii=False)
            logger.debug("Histórico salvo com sucesso")
        except Exception as e:
            logger.exception("Erro ao salvar histórico: %s", e)
            messagebox.showerror("Erro", f"Erro ao salvar histórico: {e}")

    def criar_interface(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="24", style="TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        titulo = ttk.Label(main_frame, text="Timer Tool — Ponto", style="Title.TLabel")
        titulo.grid(row=0, column=0, pady=(0, 20))

        card_projeto = ttk.Frame(main_frame, style="Card.TFrame", padding="16")
        card_projeto.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        card_projeto.grid_columnconfigure(0, weight=1)

        ttk.Label(card_projeto, text="Projeto", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        self.projeto_var = tk.StringVar()
        self.dropdown_projetos = ttk.Combobox(
            card_projeto, textvariable=self.projeto_var, state="readonly", width=42
        )
        self.dropdown_projetos.grid(row=1, column=0, pady=(0, 12))

        ttk.Label(card_projeto, text="Ou novo projeto", style="Section.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 8)
        )
        self.novo_projeto_var = tk.StringVar()
        self.entrada_novo_projeto = ttk.Entry(
            card_projeto, textvariable=self.novo_projeto_var, width=44
        )
        self.entrada_novo_projeto.grid(row=3, column=0, pady=(0, 4))

        card_ponto = ttk.Frame(main_frame, style="Card.TFrame", padding="20")
        card_ponto.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        card_ponto.grid_columnconfigure(0, weight=1)

        ttk.Label(card_ponto, text="Registro de ponto", style="Section.TLabel").grid(
            row=0, column=0, pady=(0, 12)
        )
        self.label_tempo = ttk.Label(card_ponto, text="00:00:00", style="Timer.TLabel")
        self.label_tempo.grid(row=1, column=0, pady=(0, 4))
        self.label_entrada = ttk.Label(card_ponto, text="", style="TLabel")
        self.label_entrada.grid(row=2, column=0, pady=(0, 16))

        botoes_frame = ttk.Frame(card_ponto)
        botoes_frame.grid(row=3, column=0, pady=(0, 4))
        self.btn_entrada = ttk.Button(
            botoes_frame,
            text="Ponto de Entrada",
            command=self.ponto_entrada,
            width=18,
            style="Primary.TButton",
        )
        self.btn_entrada.grid(row=0, column=0, padx=6)
        self.btn_saida = ttk.Button(
            botoes_frame,
            text="Ponto de Saída",
            command=self.ponto_saida,
            width=18,
            state="disabled",
        )
        self.btn_saida.grid(row=0, column=1, padx=6)
        self.btn_editar_ponto = ttk.Button(
            card_ponto,
            text="Editar ponto",
            command=self.abrir_editar_ponto,
            width=18,
        )
        self.btn_editar_ponto.grid(row=0, column=2, padx=6)

        self.label_total = ttk.Label(main_frame, text="", style="Total.TLabel")
        self.label_total.grid(row=3, column=0, pady=(8, 2))
        self.label_total_hoje = ttk.Label(main_frame, text="", style="Total.TLabel")
        self.label_total_hoje.grid(row=4, column=0, pady=(0, 16))

        card_relatorios = ttk.Frame(main_frame, style="Card.TFrame", padding="16")
        card_relatorios.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        card_relatorios.grid_columnconfigure(0, weight=1)

        ttk.Label(card_relatorios, text="Relatórios", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, pady=(0, 10)
        )
        self.btn_log_semanal = ttk.Button(
            card_relatorios, text="Log Semanal", command=self.gerar_log_semanal, width=14
        )
        self.btn_log_semanal.grid(row=1, column=0, padx=4, pady=4)
        self.btn_log_mensal = ttk.Button(
            card_relatorios, text="Log Mensal", command=self.gerar_log_mensal, width=14
        )
        self.btn_log_mensal.grid(row=1, column=1, padx=4, pady=4)
        self.btn_log_customizado = ttk.Button(
            card_relatorios,
            text="Log customizado",
            command=self.abrir_relatorio_customizado,
            width=14,
        )
        self.btn_log_customizado.grid(row=1, column=2, padx=4, pady=4)
        self.btn_relatorio_avancado = ttk.Button(
            card_relatorios,
            text="Relatório mensal (config.)",
            command=self.abrir_relatorio_mensal_config,
            width=22,
        )
        self.btn_relatorio_avancado.grid(row=2, column=0, columnspan=3, padx=4, pady=(4, 0))

        self.dropdown_projetos.bind("<<ComboboxSelected>>", self.atualizar_total_projeto)

    def atualizar_dropdown_projetos(self):
        projetos = sorted(self.historico.keys())
        logger.debug("Atualizando dropdown de projetos: %s", projetos)
        self.dropdown_projetos["values"] = projetos
        if projetos:
            self.dropdown_projetos.current(0)
            self.atualizar_total_projeto()

    def obter_total_hoje_projeto(self, projeto):
        """Retorna total de segundos trabalhados hoje no projeto (inclui sessão em andamento se for o mesmo)."""
        if not projeto:
            return 0.0
        total = 0.0
        if projeto in self.historico:
            hoje = datetime.now().date()
            for sessao in self.historico[projeto].get("sessoes", []):
                data_sessao = datetime.fromisoformat(sessao["data"]).date()
                if data_sessao == hoje:
                    total += sessao["duracao_segundos"]
        if self.contando and self.projeto_em_andamento == projeto and self.tempo_inicio:
            total += time.time() - self.tempo_inicio
        return total

    def atualizar_total_projeto(self, event=None):
        projeto = self.projeto_em_andamento if self.contando else self.projeto_var.get()
        if projeto:
            if projeto in self.historico:
                total_segundos = self.historico[projeto]["total_segundos"]
                horas, resto = divmod(total_segundos, 3600)
                minutos, segundos = divmod(resto, 60)
                self.label_total.config(
                    text=f"Total no projeto: {int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"
                )
            else:
                self.label_total.config(text="Total no projeto: 00:00:00")
            total_hoje = self.obter_total_hoje_projeto(projeto)
            h, r = divmod(int(total_hoje), 3600)
            m, s = divmod(r, 60)
            self.label_total_hoje.config(
                text=f"Hoje neste projeto: {h:02d}:{m:02d}:{s:02d}"
            )
        else:
            self.label_total.config(text="")
            self.label_total_hoje.config(text="")

    def obter_projeto_selecionado(self):
        novo_projeto = self.novo_projeto_var.get().strip()
        projeto_existente = self.projeto_var.get().strip()
        if novo_projeto:
            return novo_projeto
        if projeto_existente:
            return projeto_existente
        return None

    def ponto_entrada(self):
        """Registra ponto de entrada e inicia o cronômetro."""
        projeto = self.obter_projeto_selecionado()
        if not projeto:
            logger.debug("Ponto entrada ignorado: nenhum projeto selecionado")
            messagebox.showwarning(
                "Aviso", "Selecione um projeto existente ou digite um novo projeto."
            )
            return

        self.tempo_inicio = time.time()
        logger.debug("Ponto de entrada: projeto=%s tempo_inicio=%s", projeto, datetime.fromtimestamp(self.tempo_inicio))
        self.tempo_decorrido = 0
        self.contando = True
        self.projeto_em_andamento = projeto

        self.btn_entrada.config(state="disabled")
        self.dropdown_projetos.config(state="disabled")
        self.entrada_novo_projeto.config(state="disabled")
        self.btn_saida.config(state="normal")

        dt_entrada = datetime.fromtimestamp(self.tempo_inicio)
        self.label_entrada.config(text=f"Entrada: {dt_entrada.strftime('%d/%m/%Y %H:%M')}")

        self.salvar_sessao_aberta()
        self.agendar_checkpoint()
        self.atualizar_display_tempo()

    def ponto_saida(self):
        """Registra ponto de saída e salva a sessão."""
        if not self.contando:
            logger.debug("Ponto saída ignorado: contando=False")
            return

        projeto = self.projeto_em_andamento or self.obter_projeto_selecionado()
        self.contando = False
        tempo_fim = time.time()
        tempo_trabalhado = tempo_fim - self.tempo_inicio
        data_hora_inicio = datetime.fromtimestamp(self.tempo_inicio)
        data_hora_fim = datetime.fromtimestamp(tempo_fim)
        logger.debug(
            "Ponto de saída: projeto=%s duracao_seg=%.1f entrada=%s saida=%s",
            projeto, tempo_trabalhado, data_hora_inicio, data_hora_fim,
        )

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.checkpoint_id:
            self.root.after_cancel(self.checkpoint_id)
            self.checkpoint_id = None
        try:
            if os.path.exists(self.arquivo_sessao_aberta):
                os.remove(self.arquivo_sessao_aberta)
        except OSError:
            pass

        if projeto:
            sessao = {
                "data": data_hora_inicio.isoformat(),
                "data_saida": data_hora_fim.isoformat(),
                "duracao_segundos": tempo_trabalhado,
            }
            if projeto in self.historico:
                self.historico[projeto]["total_segundos"] += tempo_trabalhado
                self.historico[projeto]["sessoes"].append(sessao)
            else:
                self.historico[projeto] = {
                    "total_segundos": tempo_trabalhado,
                    "sessoes": [sessao],
                }
            self.salvar_historico()

        self.btn_entrada.config(state="normal")
        self.dropdown_projetos.config(state="readonly")
        self.entrada_novo_projeto.config(state="normal")
        self.btn_saida.config(state="disabled")
        self.label_entrada.config(text="")
        self.projeto_em_andamento = None
        self.novo_projeto_var.set("")
        self.atualizar_dropdown_projetos()
        self.label_tempo.config(text="00:00:00")

        horas, resto = divmod(int(tempo_trabalhado), 3600)
        minutos, segundos = divmod(resto, 60)
        if projeto:
            messagebox.showinfo(
                "Ponto de saída",
                f"Saída registrada para '{projeto}'.\n"
                f"Entrada: {data_hora_inicio.strftime('%H:%M')} — Saída: {data_hora_fim.strftime('%H:%M')}\n"
                f"Duração: {horas:02d}:{minutos:02d}:{segundos:02d}",
            )

    def atualizar_display_tempo(self):
        if self.contando:
            self.tempo_decorrido = time.time() - self.tempo_inicio
            horas, resto = divmod(int(self.tempo_decorrido), 3600)
            minutos, segundos = divmod(resto, 60)
            self.label_tempo.config(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
            self.atualizar_total_projeto()
            self.timer_id = self.root.after(1000, self.atualizar_display_tempo)

    def _recalcular_total_projeto(self, projeto):
        """Recalcula total_segundos do projeto a partir das sessões."""
        sessoes = self.historico[projeto].get("sessoes", [])
        self.historico[projeto]["total_segundos"] = sum(s["duracao_segundos"] for s in sessoes)

    def abrir_editar_ponto(self):
        """Abre janela para listar, editar ou excluir pontos existentes."""
        janela = tk.Toplevel(self.root)
        janela.title("Editar ponto")
        janela.geometry("820x420")
        janela.resizable(True, True)
        janela.transient(self.root)

        frame = ttk.Frame(janela, padding="16")
        frame.pack(fill=tk.BOTH, expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ttk.Label(frame, text="Pontos registrados — selecione para editar ou excluir", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )

        colunas = ("projeto", "data_entrada", "hora_entrada", "data_saida", "hora_saida", "duracao")
        tree = ttk.Treeview(frame, columns=colunas, show="headings", height=14, selectmode="browse")
        tree.heading("projeto", text="Projeto")
        tree.heading("data_entrada", text="Data entrada")
        tree.heading("hora_entrada", text="Hora entrada")
        tree.heading("data_saida", text="Data saída")
        tree.heading("hora_saida", text="Hora saída")
        tree.heading("duracao", text="Duração")
        tree.column("projeto", width=140)
        tree.column("data_entrada", width=100)
        tree.column("hora_entrada", width=80)
        tree.column("data_saida", width=100)
        tree.column("hora_saida", width=80)
        tree.column("duracao", width=80)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), pady=(0, 8))
        scroll.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 8))

        itens_para_sessao = {}

        def preencher_tree():
            for item in tree.get_children(""):
                tree.delete(item)
            itens_para_sessao.clear()
            for projeto in sorted(self.historico.keys()):
                for i, sessao in enumerate(self.historico[projeto].get("sessoes", [])):
                    di = datetime.fromisoformat(sessao["data"])
                    data_ent = di.strftime("%d/%m/%Y")
                    hora_ent = di.strftime("%H:%M")
                    if "data_saida" in sessao:
                        ds = datetime.fromisoformat(sessao["data_saida"])
                        data_sai = ds.strftime("%d/%m/%Y")
                        hora_sai = ds.strftime("%H:%M")
                    else:
                        data_sai = "-"
                        hora_sai = "-"
                    dur = self.formatar_duracao(sessao["duracao_segundos"])
                    item_id = tree.insert("", tk.END, values=(projeto, data_ent, hora_ent, data_sai, hora_sai, dur))
                    itens_para_sessao[item_id] = (projeto, i)

        preencher_tree()

        def obter_selecao():
            sel = tree.selection()
            if not sel:
                return None, None
            item_id = sel[0]
            return itens_para_sessao.get(item_id, (None, None))

        def editar():
            projeto, idx = obter_selecao()
            if projeto is None:
                messagebox.showwarning("Aviso", "Selecione um ponto na lista.")
                return
            sessao = self.historico[projeto]["sessoes"][idx]
            di = datetime.fromisoformat(sessao["data"])
            if "data_saida" in sessao:
                ds = datetime.fromisoformat(sessao["data_saida"])
            else:
                ds = di + timedelta(seconds=sessao["duracao_segundos"])
            janela_ed = tk.Toplevel(janela)
            janela_ed.title("Editar ponto")
            janela_ed.transient(janela)
            janela_ed.grab_set()
            f_ed = ttk.Frame(janela_ed, padding="20")
            f_ed.pack()
            ttk.Label(f_ed, text="Data entrada (DD/MM/AAAA):").grid(row=0, column=0, sticky=tk.W, pady=4)
            ttk.Label(f_ed, text="Hora entrada (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=4)
            ttk.Label(f_ed, text="Data saída (DD/MM/AAAA):").grid(row=2, column=0, sticky=tk.W, pady=4)
            ttk.Label(f_ed, text="Hora saída (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=4)
            v_data_ent = tk.StringVar(value=di.strftime("%d/%m/%Y"))
            v_hora_ent = tk.StringVar(value=di.strftime("%H:%M"))
            v_data_sai = tk.StringVar(value=ds.strftime("%d/%m/%Y"))
            v_hora_sai = tk.StringVar(value=ds.strftime("%H:%M"))
            ttk.Entry(f_ed, textvariable=v_data_ent, width=14).grid(row=0, column=1, padx=8, pady=4)
            ttk.Entry(f_ed, textvariable=v_hora_ent, width=8).grid(row=1, column=1, padx=8, pady=4)
            ttk.Entry(f_ed, textvariable=v_data_sai, width=14).grid(row=2, column=1, padx=8, pady=4)
            ttk.Entry(f_ed, textvariable=v_hora_sai, width=8).grid(row=3, column=1, padx=8, pady=4)

            def parse_data_hora(data_str, hora_str):
                try:
                    dt = datetime.strptime(f"{data_str.strip()} {hora_str.strip()}", "%d/%m/%Y %H:%M")
                    return dt
                except ValueError:
                    return None

            def salvar_edicao():
                di_novo = parse_data_hora(v_data_ent.get(), v_hora_ent.get())
                ds_novo = parse_data_hora(v_data_sai.get(), v_hora_sai.get())
                if di_novo is None:
                    messagebox.showerror("Erro", "Data/hora de entrada inválida. Use DD/MM/AAAA e HH:MM.")
                    return
                if ds_novo is None:
                    messagebox.showerror("Erro", "Data/hora de saída inválida. Use DD/MM/AAAA e HH:MM.")
                    return
                if ds_novo <= di_novo:
                    messagebox.showerror("Erro", "A saída deve ser posterior à entrada.")
                    return
                duracao = (ds_novo - di_novo).total_seconds()
                self.historico[projeto]["sessoes"][idx] = {
                    "data": di_novo.isoformat(),
                    "data_saida": ds_novo.isoformat(),
                    "duracao_segundos": duracao,
                }
                self._recalcular_total_projeto(projeto)
                self.salvar_historico()
                self.atualizar_dropdown_projetos()
                if self.projeto_var.get() == projeto:
                    self.atualizar_total_projeto()
                janela_ed.destroy()
                preencher_tree()
                messagebox.showinfo("Sucesso", "Ponto atualizado.")

            ttk.Button(f_ed, text="Salvar", command=salvar_edicao).grid(row=4, column=0, columnspan=2, pady=16)

        def excluir():
            projeto, idx = obter_selecao()
            if projeto is None:
                messagebox.showwarning("Aviso", "Selecione um ponto na lista.")
                return
            if not messagebox.askyesno("Confirmar", "Excluir este ponto? Esta ação não pode ser desfeita."):
                return
            self.historico[projeto]["sessoes"].pop(idx)
            if not self.historico[projeto]["sessoes"]:
                del self.historico[projeto]
            else:
                self._recalcular_total_projeto(projeto)
            self.salvar_historico()
            self.atualizar_dropdown_projetos()
            if self.projeto_var.get() == projeto:
                self.atualizar_total_projeto()
            preencher_tree()
            messagebox.showinfo("Sucesso", "Ponto excluído.")

        botoes = ttk.Frame(frame)
        botoes.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(botoes, text="Editar", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Excluir", command=excluir).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Fechar", command=janela.destroy).pack(side=tk.LEFT, padx=4)

    def filtrar_sessoes_por_periodo(self, data_inicio, data_fim, projetos=None):
        if projetos is None:
            projetos = list(self.historico.keys())
        logger.debug("Filtrando sessões: %s a %s projetos=%s", data_inicio, data_fim, projetos)
        sessoes_periodo = {}
        for projeto in projetos:
            if projeto not in self.historico:
                continue
            dados = self.historico[projeto]
            sessoes_filtradas = []
            for sessao in dados.get("sessoes", []):
                data_sessao = datetime.fromisoformat(sessao["data"])
                if data_inicio <= data_sessao <= data_fim:
                    sessoes_filtradas.append(sessao)
            if sessoes_filtradas:
                total_segundos = sum(s["duracao_segundos"] for s in sessoes_filtradas)
                sessoes_periodo[projeto] = {
                    "sessoes": sessoes_filtradas,
                    "total_segundos": total_segundos,
                }
        logger.debug("Sessões no período: %d projeto(s), totais=%s", len(sessoes_periodo), {p: d["total_segundos"] for p, d in sessoes_periodo.items()})
        return sessoes_periodo

    def formatar_duracao(self, segundos):
        horas, resto = divmod(int(segundos), 3600)
        minutos, segundos_rest = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos_rest:02d}"

    def gerar_log_semanal(self):
        hoje = datetime.now()
        data_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
        data_inicio = (hoje - timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self.exibir_log(data_inicio, data_fim, "Semanal", None)

    def gerar_log_mensal(self):
        hoje = datetime.now()
        data_fim = hoje.replace(hour=23, minute=59, second=59, microsecond=999999)
        data_inicio = (hoje - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self.exibir_log(data_inicio, data_fim, "Mensal", None)

    def abrir_relatorio_mensal_config(self):
        """Abre janela de configuração do relatório mensal com seleção de projetos e export PDF."""
        janela = tk.Toplevel(self.root)
        janela.title("Relatório mensal — Configuração")
        janela.geometry("480x420")
        janela.resizable(True, True)
        janela.transient(self.root)
        janela.grab_set()

        frame = ttk.Frame(janela, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Mês e ano", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        periodo_frame = ttk.Frame(frame)
        periodo_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 16))
        hoje = datetime.now()
        mes_var = tk.IntVar(value=hoje.month)
        ano_var = tk.IntVar(value=hoje.year)
        ttk.Spinbox(
            periodo_frame, from_=1, to=12, textvariable=mes_var, width=5
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Spinbox(
            periodo_frame, from_=2020, to=2030, textvariable=ano_var, width=6
        ).pack(side=tk.LEFT)

        ttk.Label(frame, text="Projetos a incluir no relatório", style="Section.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 8)
        )
        projetos = sorted(self.historico.keys())
        vars_projetos = {}
        inner = ttk.Frame(frame)
        inner.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 16))
        frame.grid_rowconfigure(3, weight=1)
        for i, proj in enumerate(projetos):
            vars_projetos[proj] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                inner, text=proj, variable=vars_projetos[proj]
            )
            cb.grid(row=i, column=0, sticky=tk.W, pady=2)
        if not projetos:
            ttk.Label(inner, text="Nenhum projeto no histórico.").grid(row=0, column=0, sticky=tk.W)

        def visualizar():
            mes, ano = mes_var.get(), ano_var.get()
            try:
                data_inicio = datetime(ano, mes, 1, 0, 0, 0, 0)
                if mes == 12:
                    data_fim = datetime(ano, 12, 31, 23, 59, 59, 999999)
                else:
                    data_fim = (datetime(ano, mes + 1, 1) - timedelta(seconds=1))
            except Exception:
                messagebox.showerror("Erro", "Mês/ano inválidos.")
                return
            proj_selecionados = [p for p, v in vars_projetos.items() if v.get()]
            if not proj_selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos um projeto.")
                return
            janela.withdraw()
            self.exibir_log(
                data_inicio, data_fim,
                f"Mensal {mes:02d}/{ano}",
                proj_selecionados,
                janela_parent=janela,
            )

        def exportar_pdf():
            mes, ano = mes_var.get(), ano_var.get()
            try:
                data_inicio = datetime(ano, mes, 1, 0, 0, 0, 0)
                if mes == 12:
                    data_fim = datetime(ano, 12, 31, 23, 59, 59, 999999)
                else:
                    data_fim = (datetime(ano, mes + 1, 1) - timedelta(seconds=1))
            except Exception:
                messagebox.showerror("Erro", "Mês/ano inválidos.")
                return
            proj_selecionados = [p for p, v in vars_projetos.items() if v.get()]
            if not proj_selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos um projeto.")
                return
            if not REPORTLAB_AVAILABLE:
                messagebox.showerror(
                    "Erro",
                    "Exportação PDF não disponível. Instale: pip install reportlab",
                )
                return
            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"relatorio_horas_{ano}_{mes:02d}.pdf",
            )
            if not caminho:
                return
            if self.exportar_relatorio_pdf(
                data_inicio, data_fim, proj_selecionados, caminho
            ):
                messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{caminho}")
            else:
                messagebox.showerror("Erro", "Falha ao gerar o PDF.")

        botoes = ttk.Frame(frame)
        botoes.grid(row=4, column=0, pady=(8, 0))
        ttk.Button(botoes, text="Visualizar relatório", command=visualizar).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(botoes, text="Exportar PDF", command=exportar_pdf).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(botoes, text="Fechar", command=janela.destroy).pack(side=tk.LEFT, padx=4)

    def _parse_data_br(self, texto):
        """Converte string DD/MM/AAAA em datetime. Retorna None se inválido."""
        texto = (texto or "").strip()
        if not texto:
            return None
        try:
            return datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            return None

    def abrir_relatorio_customizado(self):
        """Abre janela de relatório com período de tempo selecionado (data inicial e final)."""
        janela = tk.Toplevel(self.root)
        janela.title("Relatório customizado — Período")
        janela.geometry("480x460")
        janela.resizable(True, True)
        janela.transient(self.root)
        janela.grab_set()

        frame = ttk.Frame(janela, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Período (DD/MM/AAAA)", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        hoje = datetime.now()
        data_inicio_padrao = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        data_fim_padrao = hoje.strftime("%d/%m/%Y")
        periodo_frame = ttk.Frame(frame)
        periodo_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 4))
        ttk.Label(periodo_frame, text="De:").pack(side=tk.LEFT, padx=(0, 4))
        data_inicio_var = tk.StringVar(value=data_inicio_padrao)
        entrada_data_inicio = ttk.Entry(periodo_frame, textvariable=data_inicio_var, width=12)
        entrada_data_inicio.pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(periodo_frame, text="Até:").pack(side=tk.LEFT, padx=(0, 4))
        data_fim_var = tk.StringVar(value=data_fim_padrao)
        entrada_data_fim = ttk.Entry(periodo_frame, textvariable=data_fim_var, width=12)
        entrada_data_fim.pack(side=tk.LEFT)
        ttk.Label(frame, text="Ex.: 01/01/2025 a 31/01/2025", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 16)
        )

        ttk.Label(frame, text="Projetos a incluir no relatório", style="Section.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 8)
        )
        projetos = sorted(self.historico.keys())
        vars_projetos = {}
        inner = ttk.Frame(frame)
        inner.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 16))
        frame.grid_rowconfigure(4, weight=1)
        for i, proj in enumerate(projetos):
            vars_projetos[proj] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(inner, text=proj, variable=vars_projetos[proj])
            cb.grid(row=i, column=0, sticky=tk.W, pady=2)
        if not projetos:
            ttk.Label(inner, text="Nenhum projeto no histórico.").grid(row=0, column=0, sticky=tk.W)

        def obter_periodo():
            di = self._parse_data_br(data_inicio_var.get())
            df = self._parse_data_br(data_fim_var.get())
            if di is None:
                messagebox.showerror("Erro", "Data inicial inválida. Use DD/MM/AAAA.")
                return None, None
            if df is None:
                messagebox.showerror("Erro", "Data final inválida. Use DD/MM/AAAA.")
                return None, None
            data_inicio = di.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = df.replace(hour=23, minute=59, second=59, microsecond=999999)
            if data_inicio > data_fim:
                messagebox.showerror("Erro", "Data inicial deve ser anterior à data final.")
                return None, None
            return data_inicio, data_fim

        def visualizar():
            data_inicio, data_fim = obter_periodo()
            if data_inicio is None:
                return
            proj_selecionados = [p for p, v in vars_projetos.items() if v.get()]
            if not proj_selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos um projeto.")
                return
            janela.withdraw()
            self.exibir_log(
                data_inicio, data_fim,
                "Customizado",
                proj_selecionados,
                janela_parent=janela,
            )

        def exportar_pdf():
            data_inicio, data_fim = obter_periodo()
            if data_inicio is None:
                return
            proj_selecionados = [p for p, v in vars_projetos.items() if v.get()]
            if not proj_selecionados:
                messagebox.showwarning("Aviso", "Selecione ao menos um projeto.")
                return
            if not REPORTLAB_AVAILABLE:
                messagebox.showerror(
                    "Erro",
                    "Exportação PDF não disponível. Instale: pip install reportlab",
                )
                return
            sufixo = f"{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}"
            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"relatorio_horas_{sufixo}.pdf",
            )
            if not caminho:
                return
            if self.exportar_relatorio_pdf(
                data_inicio, data_fim, proj_selecionados, caminho
            ):
                messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{caminho}")
            else:
                messagebox.showerror("Erro", "Falha ao gerar o PDF.")

        botoes = ttk.Frame(frame)
        botoes.grid(row=5, column=0, pady=(8, 0))
        ttk.Button(botoes, text="Visualizar relatório", command=visualizar).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(botoes, text="Exportar PDF", command=exportar_pdf).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(botoes, text="Fechar", command=janela.destroy).pack(side=tk.LEFT, padx=4)

    def exportar_relatorio_pdf(self, data_inicio, data_fim, projetos, caminho):
        """Gera PDF do relatório de horas para o período e projetos indicados."""
        logger.debug("exportar_relatorio_pdf: caminho=%s projetos=%s", caminho, projetos)
        if not REPORTLAB_AVAILABLE:
            logger.debug("exportar_relatorio_pdf: reportlab não disponível")
            return False
        sessoes_periodo = self.filtrar_sessoes_por_periodo(
            data_inicio, data_fim, projetos
        )
        if not sessoes_periodo:
            logger.debug("exportar_relatorio_pdf: nenhuma sessão no período")
            return False

        doc = SimpleDocTemplate(
            caminho, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=12
        )
        elements = []
        elements.append(
            Paragraph("Relatório de Horas Trabalhadas", title_style)
        )
        elements.append(
            Paragraph(
                f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 16))

        total_geral = sum(d["total_segundos"] for d in sessoes_periodo.values())
        elements.append(
            Paragraph(
                f"Total geral: {self.formatar_duracao(total_geral)}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        for projeto in sorted(sessoes_periodo.keys()):
            dados = sessoes_periodo[projeto]
            elements.append(
                Paragraph(f"<b>{projeto}</b> — Total: {self.formatar_duracao(dados['total_segundos'])}", styles["Normal"])
            )
            table_data = [["Data", "Entrada", "Saída", "Duração"]]
            for s in sorted(dados["sessoes"], key=lambda x: x["data"]):
                di = datetime.fromisoformat(s["data"])
                entrada = di.strftime("%d/%m/%Y %H:%M")
                if "data_saida" in s:
                    ds = datetime.fromisoformat(s["data_saida"])
                    saida = ds.strftime("%H:%M")
                else:
                    saida = "-"
                dur = self.formatar_duracao(s["duracao_segundos"])
                table_data.append([entrada.split()[0], entrada.split()[1], saida, dur])
            t = Table(table_data, colWidths=[3 * cm, 2.5 * cm, 2 * cm, 2 * cm])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ]
                )
            )
            elements.append(t)
            elements.append(Spacer(1, 14))

        try:
            doc.build(elements)
            logger.debug("PDF gerado com sucesso: %s", caminho)
            return True
        except Exception as e:
            logger.exception("Falha ao gerar PDF: %s", e)
            return False

    def centralizar_janela_log(self, janela_log):
        janela_log.update_idletasks()
        largura_janela = janela_log.winfo_width()
        altura_janela = janela_log.winfo_height()
        largura_tela = janela_log.winfo_screenwidth()
        altura_tela = janela_log.winfo_screenheight()
        posicao_x = (largura_tela // 2) - (largura_janela // 2)
        posicao_y = (altura_tela // 2) - (altura_janela // 2)
        janela_log.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")

    def exibir_log(self, data_inicio, data_fim, tipo_log, projetos_filtro, janela_parent=None):
        logger.debug("exibir_log: tipo=%s periodo=%s a %s projetos_filtro=%s", tipo_log, data_inicio, data_fim, projetos_filtro)
        sessoes_periodo = self.filtrar_sessoes_por_periodo(
            data_inicio, data_fim, projetos_filtro
        )

        if not sessoes_periodo:
            logger.debug("exibir_log: nenhuma sessão no período")
            messagebox.showinfo(
                "Log " + tipo_log,
                f"Nenhuma sessão no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                + (" para os projetos selecionados." if projetos_filtro else "."),
            )
            if janela_parent:
                janela_parent.deiconify()
            return

        janela_log = tk.Toplevel(self.root)
        janela_log.title(
            f"Log {tipo_log} — {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        )
        janela_log.geometry("720x520")
        janela_log.resizable(True, True)

        janela_log.grid_rowconfigure(0, weight=1)
        janela_log.grid_columnconfigure(0, weight=1)

        frame_principal = ttk.Frame(janela_log, padding="16")
        frame_principal.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        frame_principal.grid_rowconfigure(3, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)

        ttk.Label(frame_principal, text=f"Relatório {tipo_log}", style="Title.TLabel").grid(
            row=0, column=0, pady=(0, 4)
        )
        ttk.Label(
            frame_principal,
            text=f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        ).grid(row=1, column=0, sticky=tk.N, pady=(0, 8))

        total_geral_segundos = sum(d["total_segundos"] for d in sessoes_periodo.values())
        ttk.Label(
            frame_principal,
            text=f"Total geral: {self.formatar_duracao(total_geral_segundos)}",
            style="Total.TLabel",
        ).grid(row=2, column=0, pady=(0, 12))

        canvas = tk.Canvas(frame_principal)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        frame_scrollavel = ttk.Frame(canvas)

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_scrollavel.bind("<Configure>", _on_configure)
        canvas.create_window(0, 0, window=frame_scrollavel, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        scrollbar.grid(row=3, column=1, sticky=(tk.N, tk.S))
        frame_principal.grid_columnconfigure(0, weight=1)

        for projeto, dados in sorted(sessoes_periodo.items()):
            lf = ttk.LabelFrame(frame_scrollavel, text=projeto, padding="10")
            lf.pack(fill=tk.X, pady=6, padx=4)
            ttk.Label(
                lf, text=f"Total: {self.formatar_duracao(dados['total_segundos'])}"
            ).pack(anchor=tk.W)
            for i, sessao in enumerate(
                sorted(dados["sessoes"], key=lambda x: x["data"]), 1
            ):
                data_sessao = datetime.fromisoformat(sessao["data"])
                duracao = self.formatar_duracao(sessao["duracao_segundos"])
                saida_str = ""
                if "data_saida" in sessao:
                    ds = datetime.fromisoformat(sessao["data_saida"])
                    saida_str = f" — Saída: {ds.strftime('%H:%M')}"
                texto = (
                    f"{i}. {data_sessao.strftime('%d/%m/%Y %H:%M')}{saida_str} — Duração: {duracao}"
                )
                ttk.Label(lf, text=texto).pack(anchor=tk.W)

        def fechar():
            janela_log.destroy()
            if janela_parent:
                janela_parent.deiconify()

        ttk.Button(frame_principal, text="Fechar", command=fechar).grid(
            row=4, column=0, pady=12
        )
        self.centralizar_janela_log(janela_log)


def main():
    root = tk.Tk()
    app = ContadorHoras(root)
    root.mainloop()


if __name__ == "__main__":
    main()
