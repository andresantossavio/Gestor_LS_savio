import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 26)).pack(pady=20)
