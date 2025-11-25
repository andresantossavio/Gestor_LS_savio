import customtkinter as ctk
from tkinter import ttk, messagebox
from database.crud_processos import (
criar_processo,
listar_processos,
atualizar_processo,
deletar_processo,
)
from database.crud_andamentos import (
criar_andamento,
listar_andamentos_do_processo,
atualizar_andamento,
deletar_andamento,
)
from database.crud_tarefas import (
criar_tarefa,
listar_tarefas_do_processo,
atualizar_tarefa,
deletar_tarefa,
)
from database.crud_anexos import (
criar_anexo,
listar_anexos_do_processo,
deletar_anexo,
)
from pathlib import Path
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ProcessoFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.db = controller.db

        self.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self, text="Gestão de Processos", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=5)

        self.btn_novo = ctk.CTkButton(
            button_frame,
            text="Novo Processo",
            command=lambda: controller.trocar_frame(
                lambda parent, ctrl: ProcessoFormFrame(parent, ctrl, None)
            ),
        )
        self.btn_novo.pack(side="left", padx=5)

        self.btn_editar = ctk.CTkButton(
            button_frame, text="Editar/Ver Detalhes", command=self.editar_processo
        )
        self.btn_editar.pack(side="left", padx=5)

        self.btn_deletar = ctk.CTkButton(
            button_frame, text="Deletar Processo", command=self.deletar_processo
        )
        self.btn_deletar.pack(side="left", padx=5)

        columns = (
            "ID",
            "Número",
            "Autor",
            "Réu",
            "cliente_id",
            "Fase",
            "UF",
            "Comarca",
            "Vara",
            "Status",
            "Observações",
            "Data Abertura",
            "Data Fechamento",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.bind("<Double-1>", self.duplo_clique)

        self.atualizar_lista()

    def atualizar_lista(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)

            for p in listar_processos(self.db):
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        p.id,
                        p.numero,
                        p.autor,
                        p.reu,
                        p.cliente_id,
                        p.fase,
                        p.uf,
                        p.comarca,
                        p.vara,
                        p.status,
                        p.observacoes,
                        p.data_abertura,
                        p.data_fechamento,
                    ),
                )
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar os processos do banco de dados.\n\nErro: {e}")

    def pegar_processo_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            return None
        processo_id = self.tree.item(sel[0])["values"][0]
        for p in listar_processos(self.db):
            if p.id == processo_id:
                return p
        return None

    def duplo_clique(self, event):
        self.editar_processo()

    def editar_processo(self):
        processo = self.pegar_processo_selecionado()
        if not processo:
            messagebox.showwarning("Aviso", "Selecione um processo para ver os detalhes ou editar.")
            return
        self.controller.trocar_frame(
            lambda parent, ctrl: ProcessoDetalhesFrame(parent, ctrl, processo.id))

    def deletar_processo(self):
        processo = self.pegar_processo_selecionado()
        if not processo:
            messagebox.showwarning("Aviso", "Selecione um processo para deletar.")
            return

        if messagebox.askyesno("Confirmar", "Deseja excluir este processo?"):
            deletar_processo(processo.id, self.db)
            self.atualizar_lista()

class ProcessoFormFrame(ctk.CTkFrame):
    def __init__(self, master, controller, processo):
        super().__init__(master)
        self.controller = controller
        self.processo = processo
        self.db = controller.db

        self.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = "Novo Processo" if processo is None else "Editar Processo"
        ctk.CTkLabel(
            self, text=titulo, font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        self.entry_numero = self._campo("Número:")
        self.entry_autor = self._campo("Autor:")
        self.entry_reu = self._campo("Réu:")
        self.entry_status = self._campo("Status:")
        self.entry_data = self._campo("Data Abertura (AAAA-MM-DD):")
        self.entry_obs = self._campo("Observações:")

        if processo:
            self.entry_numero.insert(0, processo.numero or "")
            self.entry_autor.insert(0, processo.autor or "")
            self.entry_reu.insert(0, processo.reu or "")
            self.entry_status.insert(0, processo.status or "")
            self.entry_data.insert(0, processo.data_abertura or "")
            self.entry_obs.insert(0, processo.observacoes or "")

        ctk.CTkButton(self, text="Salvar", command=self.salvar).pack(pady=20)
        ctk.CTkButton(
            self,
            text="Voltar",
            fg_color="gray",
            command=lambda: controller.trocar_frame(ProcessoFrame),
        ).pack(pady=5)

    def _campo(self, texto):
        ctk.CTkLabel(self, text=texto).pack(pady=3)
        entry = ctk.CTkEntry(self)
        entry.pack(pady=3)
        return entry

    def salvar(self):
        numero = self.entry_numero.get()
        autor = self.entry_autor.get()
        reu = self.entry_reu.get()
        status = self.entry_status.get()
        data = self.entry_data.get()
        obs = self.entry_obs.get()

        if not numero:
            messagebox.showwarning("Erro", "O número do processo é obrigatório.")
            return

        if self.processo:
            atualizar_processo(
                self.processo.id,
                numero=numero,
                autor=autor,
                reu=reu,
                status=status,
                data_abertura=data,
                observacoes=obs,
                db=self.db
            )
        else:
            criar_processo(
                numero=numero,
                autor=autor,
                reu=reu,
                fase=None,
                uf=None,
                comarca=None,
                vara=None,
                status=status,
                observacoes=obs,
                data_abertura=data,
                data_fechamento=None,
                cliente_id=None,
                db=self.db
            )

        messagebox.showinfo("Sucesso", "Processo salvo!")
        self.controller.trocar_frame(ProcessoFrame)

class ProcessoDetalhesFrame(ctk.CTkFrame):
    def __init__(self, master, controller, processo_id=None):
        super().__init__(master)
        self.controller = controller
        self.processo_id = None
        self.db = controller.db
        self.processo = None
        self.pack(fill="both", expand=True, padx=10, pady=10)

        top = ctk.CTkFrame(self)
        top.pack(fill="x")
        self.label_titulo = ctk.CTkLabel(
            top, text="Processo: ", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.label_titulo.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(
            top,
            text="Voltar",
            fg_color="gray",
            command=lambda: controller.trocar_frame(ProcessoFrame),
        ).pack(side="right", padx=10, pady=10)

        self.tabs = ctk.CTkTabview(self, width=800)
        self.tabs.pack(fill="both", expand=True, pady=10, padx=10)
        self.tabs.add("Dados")
        self.tabs.add("Andamentos")
        self.tabs.add("Tarefas")
        self.tabs.add("Documentos")

        if processo_id:
            self.carregar_processo(processo_id)

    def carregar_processo(self, processo_id):
        self.processo_id = processo_id
        from database.crud_processos import buscar_processo_por_id

        self.processo = buscar_processo_por_id(processo_id, self.db)
        if not self.processo:
            messagebox.showerror("Erro", "Processo não encontrado.")
            return

        self.label_titulo.configure(text=f"Processo: {self.processo.numero}")
        self._build_dados_tab()
        self._build_andamentos_tab()
        self._build_tarefas_tab()
        self._build_documentos_tab()

    def _build_dados_tab(self):
        f = self.tabs.tab("Dados")
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="Dados do Processo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Usando um grid para melhor alinhamento
        grid_frame = ctk.CTkFrame(f, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=10)

        campos = {
            "Número:": self.processo.numero, "Autor:": self.processo.autor,
            "Réu:": self.processo.reu, "Status:": self.processo.status,
            "Fase:": self.processo.fase, "UF:": self.processo.uf,
            "Comarca:": self.processo.comarca, "Vara:": self.processo.vara,
            "Data Abertura:": self.processo.data_abertura,
            "Data Fechamento:": self.processo.data_fechamento
        }

        for i, (label, valor) in enumerate(campos.items()):
            ctk.CTkLabel(grid_frame, text=label, anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            ctk.CTkLabel(grid_frame, text=valor or "N/A", anchor="w").grid(row=i, column=1, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(f, text="Observações:", anchor="w").pack(fill="x", padx=20, pady=(10, 0))
        obs_text = ctk.CTkTextbox(f, height=100)
        obs_text.pack(fill="x", expand=True, padx=20, pady=5)
        obs_text.insert("0.0", self.processo.observacoes or "")
        obs_text.configure(state="disabled") # Apenas para visualização

    def _build_andamentos_tab(self):
        f = self.tabs.tab("Andamentos")
        for w in f.winfo_children():
            w.destroy()

        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        # Adicionar comandos aos botões depois
        ctk.CTkButton(topf, text="Novo Andamento").pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Editar Andamento").pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Andamento").pack(side="left", padx=3)

        cols = ("ID", "Data", "Tipo", "Descrição", "Criado Por")
        self.tree_and = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree_and.heading(c, text=c)
            self.tree_and.column(c, width=140, anchor="center")
        self.tree_and.pack(fill="both", expand=True, pady=6)
        self._carregar_andamentos()

    def _carregar_andamentos(self):
        for row in self.tree_and.get_children():
            self.tree_and.delete(row)
        for a in listar_andamentos_do_processo(self.processo_id, self.db):
            criado_por = a.criado_por_usuario.nome if a.criado_por_usuario else ""
            descricao = (a.descricao[:80] + "...") if len(a.descricao or "") > 80 else a.descricao
            self.tree_and.insert("", "end", values=(a.id, a.data, a.tipo, descricao, criado_por))

    def _build_tarefas_tab(self):
        f = self.tabs.tab("Tarefas")
        for w in f.winfo_children():
            w.destroy()
        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        # Adicionar comandos aos botões depois
        ctk.CTkButton(topf, text="Nova Tarefa").pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Editar Tarefa").pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Tarefa").pack(side="left", padx=3)

        cols = ("ID", "Título", "Responsável", "Prazo", "Status")
        self.tree_task = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree_task.heading(c, text=c)
            self.tree_task.column(c, width=160, anchor="center")
        self.tree_task.pack(fill="both", expand=True, pady=6)
        self._carregar_tarefas()

    def _carregar_tarefas(self):
        for row in self.tree_task.get_children():
            self.tree_task.delete(row)
        for t in listar_tarefas_do_processo(self.processo_id, self.db):
            responsavel = t.responsavel.nome if t.responsavel else ""
            prazo = t.prazo.isoformat() if t.prazo else ""
            self.tree_task.insert("", "end", values=(t.id, t.titulo, responsavel, prazo, t.status))

    def _build_documentos_tab(self):
        f = self.tabs.tab("Documentos")
        for w in f.winfo_children():
            w.destroy()

        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        # Adicionar comandos aos botões depois
        ctk.CTkButton(topf, text="Upload").pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Anexo").pack(side="left", padx=3)

        cols = ("ID", "Nome", "Criado Em", "Tamanho")
        self.tree_doc = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree_doc.heading(c, text=c)
            self.tree_doc.column(c, width=200, anchor="center")
        self.tree_doc.pack(fill="both", expand=True, pady=6)
        self._carregar_anexos()

    def _carregar_anexos(self):
        for row in self.tree_doc.get_children():
            self.tree_doc.delete(row)
        for a in listar_anexos_do_processo(self.processo_id, self.db):
            criado = a.criado_em.strftime("%Y-%m-%d %H:%M")
            tamanho = f"{a.tamanho} bytes" if a.tamanho else ""
            self.tree_doc.insert("", "end", values=(a.id, a.nome_original or Path(a.caminho_arquivo).name, criado, tamanho))
