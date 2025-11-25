import customtkinter as ctk
from legacy_desktop.app_dashboard import DashboardFrame
from legacy_desktop.app_cadastros import CadastrosFrame
from legacy_desktop.app_processos import ProcessoFrame
from legacy_desktop.app_contabilidade import ContabilidadeFrame
from legacy_desktop.app_tarefas import TarefasFrame
from legacy_desktop.app_clientes import ClientesFrame
from legacy_desktop.app_config import ConfiguraçõesFrame

from database.database import Base, engine, SessionLocal
from database.models import Usuario

Base.metadata.create_all(bind=engine)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestão Leão e Savio (Legacy Desktop)")
        self.geometry("1100x650")

        self.frame_atual = None

        self.db = SessionLocal()

        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(
            self.menu_frame,
            text="Gestão Leão e Savio",
            font=("Arial", 18, "bold")
        )
        self.logo_label.pack(pady=20)

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Cadastros", self.show_cadastros),
            ("Processos", self.show_processos),
            ("Contabilidade", self.show_contabilidade),
            ("Tarefas", self.show_tarefas),
            ("Clientes", self.show_clientes),
            ("Configurações", self.show_config)
        ]

        for text, cmd in buttons:
            btn = ctk.CTkButton(self.menu_frame, text=text, command=cmd, anchor="w")
            btn.pack(fill="x", pady=5, padx=10)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.show_dashboard()

    def trocar_frame(self, frame_factory):
        if hasattr(self, "frame_atual") and self.frame_atual is not None:
            self.frame_atual.destroy()

        self.frame_atual = frame_factory(self.main_frame, self)
        self.frame_atual.pack(fill="both", expand=True)




    def show_dashboard(self):
        self.trocar_frame(DashboardFrame)

    def show_cadastros(self):
        self.trocar_frame(CadastrosFrame)

    def show_processos(self):
        self.trocar_frame(ProcessoFrame)

    def show_contabilidade(self):
        self.trocar_frame(ContabilidadeFrame)

    def show_tarefas(self):
        self.trocar_frame(TarefasFrame)

    def show_clientes(self):
        self.trocar_frame(ClientesFrame)

    def show_config(self):
        self.trocar_frame(ConfiguraçõesFrame)

if __name__ == "__main__":
    app = App()
    app.mainloop()
