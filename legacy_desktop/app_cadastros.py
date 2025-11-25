import customtkinter as ctk
from sqlalchemy.orm import Session
from database.crud_usuarios import criar_usuario, listar_usuarios, atualizar_usuario, excluir_usuario
from tkinter import messagebox

class CadastrosFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db: Session = app.db

        titulo = ctk.CTkLabel(self, text="Gestão de Usuários do Sistema",
                              font=("Arial", 20, "bold"))
        titulo.pack(pady=10)

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        lista_frame = ctk.CTkFrame(container, width=300)
        lista_frame.pack(side="left", fill="y", padx=10)

        lista_label = ctk.CTkLabel(lista_frame, text="Usuários cadastrados:",
                                   font=("Arial", 14, "bold"))
        lista_label.pack(pady=5)

        self.lista_scroll = ctk.CTkScrollableFrame(lista_frame, width=280, height=480)
        self.lista_scroll.pack(fill="both", expand=True)
        self.lista_buttons = []

        form_frame = ctk.CTkFrame(container)
        form_frame.pack(side="left", fill="both", expand=True, padx=20)

        form_title = ctk.CTkLabel(form_frame, text="Dados do usuário",
                                  font=("Arial", 16, "bold"))
        form_title.pack(pady=10)

        self.entry_nome = ctk.CTkEntry(form_frame, placeholder_text="Nome")
        self.entry_nome.pack(pady=8, fill="x")

        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="E-mail")
        self.entry_email.pack(pady=8, fill="x")

        self.entry_login = ctk.CTkEntry(form_frame, placeholder_text="Login")
        self.entry_login.pack(pady=8, fill="x")

        self.entry_senha = ctk.CTkEntry(form_frame, placeholder_text="Senha (0000 padrão)", show="*")
        self.entry_senha.pack(pady=8, fill="x")

        self.entry_perfil = ctk.CTkOptionMenu(
            form_frame,
            values=["Administrador", "Usuário comum"]
        )
        self.entry_perfil.pack(pady=8)

        botoes_frame = ctk.CTkFrame(form_frame)
        botoes_frame.pack(pady=15)

        ctk.CTkButton(botoes_frame, text="Novo", command=self.novo_usuario).grid(row=0, column=0, padx=5)
        ctk.CTkButton(botoes_frame, text="Salvar", command=self.salvar_usuario).grid(row=0, column=1, padx=5)
        ctk.CTkButton(botoes_frame, text="Excluir", command=self.remover_usuario).grid(row=0, column=2, padx=5)

        self.usuario_atual_id = None
        self.carregar_lista()

    def carregar_lista(self):
        for btn in self.lista_buttons:
            btn.destroy()
        self.lista_buttons.clear()

        usuarios = listar_usuarios(self.db)
        for u in usuarios:
            btn = ctk.CTkButton(self.lista_scroll, text=f"{u.id} - {u.nome}", width=260,
                                 command=lambda user_id=u.id: self.selecionar_usuario(user_id))
            btn.pack(pady=2)
            self.lista_buttons.append(btn)

    def selecionar_usuario(self, user_id):
        usuario = self.db.query(listar_usuarios(self.db)[0].__class__).filter_by(id=user_id).first()
        if not usuario:
            return
        self.usuario_atual_id = user_id
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, usuario.nome)
        self.entry_email.delete(0, "end")
        self.entry_email.insert(0, usuario.email or "")
        self.entry_login.delete(0, "end")
        self.entry_login.insert(0, usuario.login)
        self.entry_perfil.set(usuario.perfil)
        self.entry_senha.delete(0, "end")

    def novo_usuario(self):
        self.usuario_atual_id = None
        self.entry_nome.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_login.delete(0, "end")
        self.entry_senha.delete(0, "end")
        self.entry_perfil.set("Usuário comum")

    def salvar_usuario(self):
        nome = self.entry_nome.get()
        login = self.entry_login.get()
        email = self.entry_email.get()
        senha = self.entry_senha.get()
        perfil = self.entry_perfil.get()

        if not nome or not login:
            messagebox.showwarning("Atenção", "Nome e login são obrigatórios")
            return

        if self.usuario_atual_id:
            atualizar_usuario(self.db, self.usuario_atual_id, nome, email, login, senha, perfil)
        else:
            criar_usuario(self.db, nome, email, login, senha, perfil)

        self.carregar_lista()
        self.novo_usuario()

    def remover_usuario(self):
        if self.usuario_atual_id:
            excluir_usuario(self.db, self.usuario_atual_id)
            self.carregar_lista()
            self.novo_usuario()
