import customtkinter as ctk
from tkinter import ttk, messagebox
from database.crud_clientes import (
    criar_cliente,
    listar_clientes,
    atualizar_cliente,
    deletar_cliente
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ClientesFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        # Armazena a sessão do banco de dados passada pelo controller (App)
        self.db = controller.db

        self.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self,
            text="Gestão de Clientes",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=5)

        self.btn_novo = ctk.CTkButton(
            button_frame,
            text="Novo Cliente",
            command=lambda: controller.trocar_frame(
                lambda parent, ctrl: ClienteFormFrame(parent, ctrl, None)
            )
        )
        self.btn_novo.pack(side="left", padx=5)

        self.btn_editar = ctk.CTkButton(
            button_frame, text="Editar Cliente", command=self.editar_cliente
        )
        self.btn_editar.pack(side="left", padx=5)

        self.btn_deletar = ctk.CTkButton(
            button_frame, text="Deletar Cliente", command=self.deletar_cliente
        )
        self.btn_deletar.pack(side="left", padx=5)

        columns = ("ID", "Nome", "CPF/CNPJ", "Telefone", "Email")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.bind("<Double-1>", self.duplo_clique)

        self.atualizar_lista()

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in listar_clientes(self.db):
            self.tree.insert(
                "",
                "end",
                values=(c.id, c.nome, c.cpf_cnpj, c.telefone, c.email)
            )

    def pegar_cliente(self):
        sel = self.tree.selection()
        if not sel:
            return None
        cliente_id = self.tree.item(sel[0])["values"][0]
        for c in listar_clientes(self.db):
            if c.id == cliente_id:
                return c
        return None

    def editar_cliente(self):
        cliente = self.pegar_cliente()
        if not cliente:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return

        self.controller.trocar_frame(
            lambda parent, ctrl: ClienteFormFrame(parent, ctrl, cliente)
        )

    def duplo_clique(self, event):
        self.editar_cliente()

    def deletar_cliente(self):
        cliente = self.pegar_cliente()
        if not cliente:
            messagebox.showwarning("Aviso", "Selecione um cliente para deletar.")
            return

        if messagebox.askyesno("Confirmar", "Deseja deletar este cliente?"):
            deletar_cliente(cliente.id, self.db)
            self.atualizar_lista()


class ClienteFormFrame(ctk.CTkFrame):
    def __init__(self, master, controller, cliente):
        super().__init__(master)
        self.controller = controller
        self.cliente = cliente
        self.db = controller.db

        self.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = "Novo Cliente" if cliente is None else "Editar Cliente"
        ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        self.entry_nome = self._campo("Nome:")
        self.entry_cpf = self._campo("CPF/CNPJ:")
        self.entry_tel = self._campo("Telefone:")
        self.entry_email = self._campo("Email:")

        if cliente:
            self.entry_nome.insert(0, cliente.nome or "")
            self.entry_cpf.insert(0, cliente.cpf_cnpj or "")
            self.entry_tel.insert(0, cliente.telefone or "")
            self.entry_email.insert(0, cliente.email or "")

        ctk.CTkButton(self, text="Salvar", command=self.salvar).pack(pady=20)
        ctk.CTkButton(
            self,
            text="Voltar",
            fg_color="gray",
            command=lambda: controller.trocar_frame(ClientesFrame)
        ).pack(pady=5)

    def _campo(self, texto):
        ctk.CTkLabel(self, text=texto).pack(pady=2)
        entry = ctk.CTkEntry(self)
        entry.pack(pady=3)
        return entry

    def salvar(self):
        nome = self.entry_nome.get()
        cpf = self.entry_cpf.get()
        tel = self.entry_tel.get()
        email = self.entry_email.get()

        if not nome or not cpf:
            messagebox.showwarning("Erro", "Nome e CPF são obrigatórios.")
            return

        if self.cliente:
            atualizar_cliente(self.cliente.id, nome, cpf, tel, email, self.db)
        else:
            criar_cliente(nome, cpf, tel, email, self.db)

        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso.")
        self.controller.trocar_frame(ClientesFrame)
