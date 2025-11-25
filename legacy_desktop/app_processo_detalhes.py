    def _abrir_editor_dados(self):
        f = self.tabs.tab("Dados")
        for w in f.winfo_children():
            w.destroy()

        ctk.CTkLabel(f, text="Editar Processo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        entry_num = ctk.CTkEntry(f); entry_num.insert(0, self.processo.numero or ""); entry_num.pack(pady=3)
        entry_autor = ctk.CTkEntry(f); entry_autor.insert(0, self.processo.autor or ""); entry_autor.pack(pady=3)
        entry_reu = ctk.CTkEntry(f); entry_reu.insert(0, self.processo.reu or ""); entry_reu.pack(pady=3)
        entry_status = ctk.CTkEntry(f); entry_status.insert(0, self.processo.status or ""); entry_status.pack(pady=3)
        txt_obs = ctk.CTkTextbox(f, width=700, height=200); txt_obs.pack(pady=5); txt_obs.insert("0.0", self.processo.observacoes or "")

        def salvar():
            atualizar_processo(
                self.processo.id,
                numero=entry_num.get(),
                autor=entry_autor.get(),
                reu=entry_reu.get(),
                status=entry_status.get(),
                observacoes=txt_obs.get("0.0", "end").strip()
            )
            messagebox.showinfo("Sucesso", "Processo atualizado.")
            self.carregar_processo(self.processo_id)

        ctk.CTkButton(f, text="Salvar", command=salvar).pack(pady=6)
        ctk.CTkButton(f, text="Cancelar", fg_color="gray", command=lambda: self._build_dados_tab()).pack(pady=2)

    def _build_andamentos_tab(self):
        f = self.tabs.tab("Andamentos")
        for w in f.winfo_children():
            w.destroy()

        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        ctk.CTkButton(topf, text="Novo Andamento", command=self._novo_andamento).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Editar Andamento", command=self._editar_andamento).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Andamento", command=self._excluir_andamento).pack(side="left", padx=3)

        cols = ("ID", "Data", "Tipo", "Descrição", "Criado Por")
        self.tree_and = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree_and.heading(c, text=c)
            self.tree_and.column(c, width=140, anchor="center")
        self.tree_and.pack(fill="both", expand=True, pady=6)

        self._carregar_andamentos()
        self.tree_and.bind("<Double-1>", lambda e: self._editar_andamento())

    def _carregar_andamentos(self):
        for row in self.tree_and.get_children():
            self.tree_and.delete(row)
        for a in listar_andamentos_do_processo(self.processo_id):
            criado_por = a.criado_por_usuario.nome if a.criado_por_usuario else ""
            descricao = (a.descricao[:80] + "...") if len(a.descricao or "") > 80 else a.descricao
            self.tree_and.insert("", "end", values=(a.id, a.data, a.tipo, descricao, criado_por))

    def _build_tarefas_tab(self):
        f = self.tabs.tab("Tarefas")
        for w in f.winfo_children():
            w.destroy()
        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        ctk.CTkButton(topf, text="Nova Tarefa", command=self._nova_tarefa).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Editar Tarefa", command=self._editar_tarefa).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Tarefa", command=self._excluir_tarefa).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Marcar Concluída", command=self._marcar_concluida).pack(side="left", padx=3)

        cols = ("ID", "Título", "Responsável", "Prazo", "Status")
        self.tree_task = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree_task.heading(c, text=c)
            self.tree_task.column(c, width=160, anchor="center")
        self.tree_task.pack(fill="both", expand=True, pady=6)

        self._carregar_tarefas()
        self.tree_task.bind("<Double-1>", lambda e: self._editar_tarefa())

    def _carregar_tarefas(self):
        for row in self.tree_task.get_children():
            self.tree_task.delete(row)
        for t in listar_tarefas_do_processo(self.processo_id):
            responsavel = t.responsavel.nome if t.responsavel else ""
            prazo = t.prazo.isoformat() if t.prazo else ""
            self.tree_task.insert("", "end", values=(t.id, t.titulo, responsavel, prazo, t.status))

    def _build_documentos_tab(self):
        f = self.tabs.tab("Documentos")
        for w in f.winfo_children():
            w.destroy()

        topf = ctk.CTkFrame(f); topf.pack(fill="x", pady=3)
        ctk.CTkButton(topf, text="Upload", command=self._upload_arquivo).pack(side="left", padx=3)
        ctk.CTkButton(topf, text="Excluir Anexo", command=self._excluir_anexo).pack(side="left", padx=3)

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
        for a in listar_anexos_do_processo(self.processo_id):
            criado = a.criado_em.strftime("%Y-%m-%d %H:%M")
            tamanho = f"{a.tamanho} bytes" if a.tamanho else ""
            self.tree_doc.insert("", "end", values=(a.id, a.nome_original or Path(a.caminho_arquivo).name, criado, tamanho))

