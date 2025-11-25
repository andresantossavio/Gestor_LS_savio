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
        processo = self.pegar_processo_selecionado()
        if processo:
            self.controller.trocar_frame(
                lambda parent, ctrl: ProcessoDetalhesFrame(parent, ctrl, processo.id)
            )

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
