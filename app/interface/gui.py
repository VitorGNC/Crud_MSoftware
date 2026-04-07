from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from app.models.usuario import UsuarioErro
from app.patterns.factory import CommandFactory
from app.patterns.observer import EventoSatelite, LogSatelliteObserver, SatelliteEventBus
from app.patterns.receiver import NoteReceiver
from app.patterns.sender import CommandSender
from app.services.note_service import NoteService
from app.services.satellite_service import SatelliteService
from app.services.user_service import UserService

_SIDEBAR_BG = "#1a2e1a"
_SIDEBAR_BTN_BG = "#2d4a2d"
_SIDEBAR_BTN_HOVER = "#3d6b3d"
_SIDEBAR_FG = "#f0f0f0"
_ACCENT = "#7ec850"
_APP_BG = "#111111"


class NotesAppGUI:
    def __init__(
        self,
        sender: CommandSender,
        receiver: NoteReceiver,
        note_service: NoteService,
        user_service: UserService,
        talhao_service=None,
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.factory = CommandFactory(receiver)
        self.note_service = note_service
        self.user_service = user_service
        self.talhao_service = talhao_service
        self.satellite_service = satellite_service
        self.current_user = None
        self.current_note_id: Optional[str] = None
        self.index_to_note: Dict[int, str] = {}
        self.index_to_talhao: Dict[int, str] = {}
        self.panels: Dict[str, tk.Frame] = {}

        self.root = tk.Tk()
        self.root.title("RigTech")
        self.root.geometry("1100x650")
        self.root.configure(bg=_APP_BG)

        self.login_frame = ttk.Frame(self.root, padding=24)
        self.main_frame = tk.Frame(self.root, bg=_APP_BG)

        self._setup_styles()
        self._build_login_frame()
        self._build_main_frame()
        self._show_login()

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=_APP_BG)
        style.configure("TLabel", background=_APP_BG, foreground="#f5f5f5")
        style.configure("TButton", padding=8)
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        style.configure(
            "Content.TLabel",
            background=_APP_BG,
            foreground="#f5f5f5",
        )

    # ------------------------------------------------------------------ login

    def _build_login_frame(self) -> None:
        ttk.Label(self.login_frame, text="RigTech", style="Header.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )

        self.login_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.idade_var = tk.StringVar()
        self.senha_registro_var = tk.StringVar()
        self.login_registro_var = tk.StringVar()

        ttk.Label(self.login_frame, text="Login").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.login_var, width=30).grid(
            row=1, column=1, pady=4
        )

        ttk.Label(self.login_frame, text="Senha").grid(row=2, column=0, sticky="w")
        ttk.Entry(
            self.login_frame, textvariable=self.senha_var, show="*", width=30
        ).grid(row=2, column=1, pady=4)

        ttk.Button(self.login_frame, text="Entrar", command=self._handle_login).grid(
            row=3, column=0, columnspan=2, pady=(12, 24), sticky="ew"
        )

        ttk.Separator(self.login_frame, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=12
        )

        ttk.Label(
            self.login_frame, text="Registrar novo usuario", style="Header.TLabel"
        ).grid(row=5, column=0, columnspan=2, pady=(8, 12))

        ttk.Label(self.login_frame, text="Email").grid(row=6, column=0, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.email_var, width=30).grid(
            row=6, column=1, pady=4
        )

        ttk.Label(self.login_frame, text="Nome").grid(row=7, column=0, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.nome_var, width=30).grid(
            row=7, column=1, pady=4
        )

        ttk.Label(self.login_frame, text="Idade").grid(row=8, column=0, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.idade_var, width=30).grid(
            row=8, column=1, pady=4
        )

        ttk.Label(self.login_frame, text="Login").grid(row=9, column=0, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.login_registro_var, width=30).grid(
            row=9, column=1, pady=4
        )

        ttk.Label(self.login_frame, text="Senha").grid(row=10, column=0, sticky="w")
        ttk.Entry(
            self.login_frame, textvariable=self.senha_registro_var, show="*", width=30
        ).grid(row=10, column=1, pady=4)

        ttk.Button(
            self.login_frame, text="Registrar", command=self._handle_register
        ).grid(row=11, column=0, columnspan=2, pady=(12, 0), sticky="ew")

    # ------------------------------------------------------------------ main

    def _build_main_frame(self) -> None:
        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self) -> None:
        sidebar = tk.Frame(self.main_frame, width=200, bg=_SIDEBAR_BG)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        tk.Label(
            sidebar,
            text="RigTech",
            bg=_SIDEBAR_BG,
            fg=_ACCENT,
            font=("Helvetica", 18, "bold"),
            pady=20,
        ).pack(fill="x")

        tk.Frame(sidebar, bg="#3d6b3d", height=1).pack(fill="x", padx=12, pady=(0, 16))

        nav_items = [
            ("Anotacoes", "notes"),
            ("Upload Imagem Drone", "upload_drone"),
            ("Mostrar Shapefile", "shapefile"),
            ("Mostrar Talhoes", "talhoes"),
            ("Criar Talhao", "criar_talhao"),
            ("Processar", "processar"),
            ("Mostrar Dados", "dados"),
        ]

        for label, panel_name in nav_items:
            btn = tk.Button(
                sidebar,
                text=label,
                bg=_SIDEBAR_BTN_BG,
                fg=_SIDEBAR_FG,
                activebackground=_SIDEBAR_BTN_HOVER,
                activeforeground=_SIDEBAR_FG,
                relief="flat",
                bd=0,
                font=("Helvetica", 11),
                anchor="w",
                padx=16,
                pady=10,
                cursor="hand2",
                command=lambda n=panel_name: self._show_panel(n),
            )
            btn.pack(fill="x", pady=1)

    def _build_content_area(self) -> None:
        self.content_area = tk.Frame(self.main_frame, bg=_APP_BG)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.panels["home"] = self._build_home_panel()
        self.panels["notes"] = self._build_notes_panel()
        self.panels["upload_drone"] = self._build_upload_drone_panel()
        self.panels["shapefile"] = self._build_placeholder_panel("Mostrar Shapefile")
        self.panels["talhoes"] = self._build_talhoes_panel()
        self.panels["criar_talhao"] = self._build_criar_talhao_panel()
        self.panels["processar"] = self._build_placeholder_panel("Processar")
        self.panels["dados"] = self._build_placeholder_panel("Mostrar Dados")

    def _build_home_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)
        tk.Label(
            panel,
            text="RigTech",
            bg=_APP_BG,
            fg=_ACCENT,
            font=("Helvetica", 52, "bold"),
        ).place(relx=0.5, rely=0.42, anchor="center")
        tk.Label(
            panel,
            text="Plataforma de Analise Agricola",
            bg=_APP_BG,
            fg="#888888",
            font=("Helvetica", 16),
        ).place(relx=0.5, rely=0.55, anchor="center")
        return panel

    def _build_placeholder_panel(self, title: str) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)
        tk.Label(
            panel,
            text=title,
            bg=_APP_BG,
            fg="#f5f5f5",
            font=("Helvetica", 20, "bold"),
        ).place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(
            panel,
            text="Em desenvolvimento",
            bg=_APP_BG,
            fg="#555555",
            font=("Helvetica", 12),
        ).place(relx=0.5, rely=0.53, anchor="center")
        return panel

    def _build_criar_talhao_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)
        inner = ttk.Frame(panel, padding=32)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            inner, text="Criar Talhao", bg=_APP_BG, fg="#f5f5f5",
            font=("Helvetica", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        campos = [
            ("Nome:", "t_nome"),
            ("Variedade de Cana:", "t_variedade"),
            ("Idade (anos):", "t_idade"),
            ("Ultima Colheita (AAAA-MM-DD):", "t_ultima_colheita"),
            ("Solo:", "t_solo"),
            ("Previsao Colheita (AAAA-MM-DD):", "t_previsao"),
        ]
        self._talhao_vars: Dict[str, tk.StringVar] = {}
        for row, (label, key) in enumerate(campos, start=1):
            ttk.Label(inner, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 12))
            var = tk.StringVar()
            self._talhao_vars[key] = var
            ttk.Entry(inner, textvariable=var, width=36).grid(row=row, column=1, pady=4, sticky="ew")

        # Status combobox
        ttk.Label(inner, text="Status:").grid(row=7, column=0, sticky="w", pady=4, padx=(0, 12))
        self._talhao_status_var = tk.StringVar(value="Ativo")
        status_cb = ttk.Combobox(
            inner, textvariable=self._talhao_status_var, width=33,
            values=["Ativo", "Em colheita", "Pousio", "Replantio"], state="readonly",
        )
        status_cb.grid(row=7, column=1, pady=4, sticky="ew")

        # Irrigação checkbox
        self._talhao_irrigacao_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            inner, text="Irrigacao", variable=self._talhao_irrigacao_var,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=8)

        # Botões
        btn_frame = ttk.Frame(inner)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(12, 0), sticky="w")

        tk.Button(
            btn_frame, text="Salvar Talhao",
            bg="#1a5c1a", fg=_SIDEBAR_FG,
            activebackground="#237a23", activeforeground=_SIDEBAR_FG,
            relief="flat", font=("Helvetica", 11), padx=16, pady=8, cursor="hand2",
            command=self._salvar_talhao,
        ).pack(side="left", padx=(0, 12))

        tk.Button(
            btn_frame, text="Importar JSON",
            bg=_SIDEBAR_BTN_BG, fg=_SIDEBAR_FG,
            activebackground=_SIDEBAR_BTN_HOVER, activeforeground=_SIDEBAR_FG,
            relief="flat", font=("Helvetica", 11), padx=16, pady=8, cursor="hand2",
            command=self._importar_talhoes_json,
        ).pack(side="left")

        self._talhao_status_msg = tk.StringVar(value="")
        tk.Label(
            inner, textvariable=self._talhao_status_msg,
            bg=_APP_BG, fg=_ACCENT, font=("Helvetica", 10),
        ).grid(row=10, column=0, columnspan=2, pady=(12, 0), sticky="w")

        return panel

    def _salvar_talhao(self) -> None:
        if not self.talhao_service:
            return
        try:
            idade = int(self._talhao_vars["t_idade"].get() or 0)
        except ValueError:
            self._talhao_status_msg.set("Idade deve ser um numero inteiro.")
            return
        try:
            self.talhao_service.criar_talhao(
                nome=self._talhao_vars["t_nome"].get(),
                variedade_cana=self._talhao_vars["t_variedade"].get(),
                idade=idade,
                ultima_colheita=self._talhao_vars["t_ultima_colheita"].get(),
                solo=self._talhao_vars["t_solo"].get(),
                status=self._talhao_status_var.get(),
                previsao_colheita=self._talhao_vars["t_previsao"].get(),
                irrigacao=self._talhao_irrigacao_var.get(),
            )
        except ValueError as exc:
            self._talhao_status_msg.set(str(exc))
            return
        # Limpa formulário
        for var in self._talhao_vars.values():
            var.set("")
        self._talhao_status_var.set("Ativo")
        self._talhao_irrigacao_var.set(False)
        self._talhao_status_msg.set("Talhao salvo com sucesso.")

    def _importar_talhoes_json(self) -> None:
        if not self.talhao_service:
            return
        path = filedialog.askopenfilename(
            title="Selecione arquivo JSON de talhoes",
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return
        try:
            criados, erros = self.talhao_service.importar_json(path)
        except Exception as exc:
            self._talhao_status_msg.set(f"Erro ao ler arquivo: {exc}")
            return
        msg = f"{criados} talhao(es) importado(s)."
        if erros:
            msg += f" {len(erros)} erro(s): {erros[0]}"
        self._talhao_status_msg.set(msg)

    def _build_talhoes_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)
        inner = ttk.Frame(panel, padding=16)
        inner.pack(fill="both", expand=True)

        tk.Label(
            inner, text="Talhoes", bg=_APP_BG, fg="#f5f5f5",
            font=("Helvetica", 18, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        body = ttk.Frame(inner)
        body.pack(fill="both", expand=True)

        # Esquerda — lista
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=(0, 16))

        self.talhoes_list = tk.Listbox(left, width=28, height=22, bg="#1c1c1c", fg="#f5f5f5",
                                        selectbackground=_SIDEBAR_BTN_HOVER, relief="flat")
        self.talhoes_list.pack(side="left", fill="y")
        self.talhoes_list.bind("<<ListboxSelect>>", self._select_talhao)

        scroll = ttk.Scrollbar(left, orient="vertical", command=self.talhoes_list.yview)
        scroll.pack(side="right", fill="y")
        self.talhoes_list.configure(yscrollcommand=scroll.set)

        # Direita — detalhes
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True)

        self._talhao_detail_labels: Dict[str, tk.StringVar] = {}
        detail_fields = [
            ("Nome", "d_nome"),
            ("Variedade de Cana", "d_variedade"),
            ("Idade (anos)", "d_idade"),
            ("Ultima Colheita", "d_ultima_colheita"),
            ("Solo", "d_solo"),
            ("Status", "d_status"),
            ("Previsao Colheita", "d_previsao"),
            ("Irrigacao", "d_irrigacao"),
            ("Criado em", "d_criado_em"),
        ]
        for i, (label, key) in enumerate(detail_fields):
            ttk.Label(right, text=f"{label}:", font=("Helvetica", 10, "bold")).grid(
                row=i, column=0, sticky="w", pady=5, padx=(0, 12)
            )
            var = tk.StringVar(value="—")
            self._talhao_detail_labels[key] = var
            ttk.Label(right, textvariable=var, font=("Helvetica", 10)).grid(
                row=i, column=1, sticky="w", pady=5
            )

        return panel

    def _refresh_talhoes(self) -> None:
        if not self.talhao_service:
            return
        self.talhoes_list.delete(0, tk.END)
        self.index_to_talhao.clear()
        for idx, t in enumerate(self.talhao_service.listar_talhoes()):
            self.talhoes_list.insert(idx, t.nome)
            self.index_to_talhao[idx] = t.talhao_id
        for var in self._talhao_detail_labels.values():
            var.set("—")

    def _select_talhao(self, _event) -> None:
        selection = self.talhoes_list.curselection()
        if not selection:
            return
        talhao_id = self.index_to_talhao.get(selection[0])
        if not talhao_id or not self.talhao_service:
            return
        t = self.talhao_service.get_talhao(talhao_id)
        if not t:
            return
        self._talhao_detail_labels["d_nome"].set(t.nome)
        self._talhao_detail_labels["d_variedade"].set(t.variedade_cana)
        self._talhao_detail_labels["d_idade"].set(str(t.idade))
        self._talhao_detail_labels["d_ultima_colheita"].set(t.ultima_colheita)
        self._talhao_detail_labels["d_solo"].set(t.solo)
        self._talhao_detail_labels["d_status"].set(t.status)
        self._talhao_detail_labels["d_previsao"].set(t.previsao_colheita)
        self._talhao_detail_labels["d_irrigacao"].set("Sim" if t.irrigacao else "Nao")
        self._talhao_detail_labels["d_criado_em"].set(t.criado_em.strftime("%d/%m/%Y %H:%M"))

    def _build_upload_drone_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)

        tk.Label(
            panel,
            text="Upload de Imagem de Drone",
            bg=_APP_BG,
            fg="#f5f5f5",
            font=("Helvetica", 20, "bold"),
        ).pack(pady=(60, 4))

        tk.Label(
            panel,
            text="Formatos suportados: GeoTIFF (.tif, .tiff) | Tamanho maximo: 25 GB",
            bg=_APP_BG,
            fg="#888888",
            font=("Helvetica", 10),
        ).pack(pady=(0, 32))

        # Área de drop / seleção
        drop_frame = tk.Frame(panel, bg="#1c1c1c", bd=2, relief="groove", width=500, height=160)
        drop_frame.pack(pady=(0, 24))
        drop_frame.pack_propagate(False)

        tk.Label(
            drop_frame,
            text="Clique em 'Selecionar Arquivo' para escolher\numa imagem georreferenciada de drone",
            bg="#1c1c1c",
            fg="#555555",
            font=("Helvetica", 12),
            justify="center",
        ).place(relx=0.5, rely=0.4, anchor="center")

        self.drone_filename_var = tk.StringVar(value="Nenhum arquivo selecionado")
        tk.Label(
            drop_frame,
            textvariable=self.drone_filename_var,
            bg="#1c1c1c",
            fg=_ACCENT,
            font=("Helvetica", 10, "italic"),
        ).place(relx=0.5, rely=0.72, anchor="center")

        # Botões
        btn_frame = tk.Frame(panel, bg=_APP_BG)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="Selecionar Arquivo",
            bg=_SIDEBAR_BTN_BG,
            fg=_SIDEBAR_FG,
            activebackground=_SIDEBAR_BTN_HOVER,
            activeforeground=_SIDEBAR_FG,
            relief="flat",
            font=("Helvetica", 11),
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._select_drone_file,
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame,
            text="Enviar",
            bg="#1a5c1a",
            fg=_SIDEBAR_FG,
            activebackground="#237a23",
            activeforeground=_SIDEBAR_FG,
            relief="flat",
            font=("Helvetica", 11),
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._upload_drone_file,
        ).pack(side="left", padx=8)

        self.drone_status_var = tk.StringVar(value="")
        tk.Label(
            panel,
            textvariable=self.drone_status_var,
            bg=_APP_BG,
            fg=_ACCENT,
            font=("Helvetica", 11),
        ).pack(pady=(20, 0))

        self._drone_selected_path: Optional[str] = None
        return panel

    def _select_drone_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione imagem de drone",
            filetypes=[("GeoTIFF", "*.tif *.tiff"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return
        self._drone_selected_path = path
        filename = path.split("/")[-1].split("\\")[-1]
        self.drone_filename_var.set(filename)
        self.drone_status_var.set("")

    def _upload_drone_file(self) -> None:
        import json
        import shutil
        from datetime import datetime
        from pathlib import Path

        if not self._drone_selected_path:
            messagebox.showwarning("Upload", "Selecione um arquivo antes de enviar.")
            return

        dest_dir = Path("data/drone_images")
        dest_dir.mkdir(parents=True, exist_ok=True)

        src = Path(self._drone_selected_path)
        dest = dest_dir / src.name

        # Se já existe, adiciona timestamp para não sobrescrever
        if dest.exists():
            stem = src.stem
            suffix = src.suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = dest_dir / f"{stem}_{timestamp}{suffix}"

        self.drone_status_var.set("Copiando arquivo...")
        self.root.update()

        shutil.copy2(str(src), str(dest))

        # Registra no JSON de persistência
        registry_path = Path("data/drone_uploads.json")
        registry: list = []
        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                registry = []

        registry.append({
            "filename": dest.name,
            "original_path": str(src),
            "saved_path": str(dest),
            "uploaded_by": self.current_user.login if self.current_user else "unknown",
            "uploaded_at": datetime.now().isoformat(),
        })
        registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        self.drone_status_var.set(f"Salvo em data/drone_images/{dest.name}")

    def _build_notes_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)
        inner = ttk.Frame(panel, padding=16)
        inner.pack(fill="both", expand=True)

        top_bar = ttk.Frame(inner)
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text="Minhas notas", style="Header.TLabel").pack(side="left")

        body = ttk.Frame(inner)
        body.pack(fill="both", expand=True, pady=12)

        left = ttk.Frame(body)
        left.pack(side="left", fill="y")
        self.notes_list = tk.Listbox(left, width=32, height=25)
        self.notes_list.pack(side="left", fill="y")
        self.notes_list.bind("<<ListboxSelect>>", self._select_note)
        note_scroll = ttk.Scrollbar(left, orient="vertical", command=self.notes_list.yview)
        note_scroll.pack(side="right", fill="y")
        self.notes_list.configure(yscrollcommand=note_scroll.set)

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=16)

        ttk.Label(right, text="Titulo").pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.title_var).pack(fill="x", pady=(0, 8))

        ttk.Label(right, text="Conteudo").pack(anchor="w")
        self.content_text = tk.Text(right, height=12)
        self.content_text.pack(fill="both", expand=True)

        attachments_frame = ttk.Frame(right)
        attachments_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(attachments_frame, text="Anexos").pack(anchor="w")
        self.attachments_list = tk.Listbox(attachments_frame, height=4)
        self.attachments_list.pack(fill="x")

        buttons = ttk.Frame(right)
        buttons.pack(fill="x", pady=12)
        ttk.Button(buttons, text="Nova nota", command=self._new_note).pack(side="left", padx=4)
        ttk.Button(buttons, text="Salvar", command=self._save_note).pack(side="left", padx=4)
        ttk.Button(buttons, text="Anexar arquivo", command=self._attach_file).pack(side="left", padx=4)
        ttk.Button(buttons, text="Excluir", command=self._delete_note).pack(side="left", padx=4)
        ttk.Button(buttons, text="Desfazer", command=self._undo).pack(side="left", padx=4)

        history_frame = ttk.Frame(right)
        history_frame.pack(fill="both", expand=False)
        ttk.Label(history_frame, text="Historico (memento)").pack(anchor="w")
        self.history_box = tk.Listbox(history_frame, height=5)
        self.history_box.pack(fill="x")

        return panel

    # ---------------------------------------------------------- navigation

    def _show_panel(self, name: str) -> None:
        for panel in self.panels.values():
            panel.place_forget()
        self.panels[name].place(relwidth=1, relheight=1)
        if name == "notes":
            self._refresh_notes()
        elif name == "talhoes":
            self._refresh_talhoes()

    def _show_login(self) -> None:
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def _show_main(self) -> None:
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self._show_panel("home")

    # ---------------------------------------------------------- auth handlers

    def _handle_login(self) -> None:
        try:
            usuario = self.user_service.autenticar(
                self.login_var.get(), self.senha_var.get()
            )
        except UsuarioErro as exc:
            messagebox.showerror("Login", str(exc))
            return
        self.current_user = usuario
        self.root.title(f"RigTech - {usuario.login}")
        self._show_main()

    def _handle_register(self) -> None:
        try:
            idade = int(self.idade_var.get()) if self.idade_var.get() else 0
        except ValueError:
            messagebox.showerror("Registro", "Idade invalida")
            return
        try:
            usuario = self.user_service.registrar(
                login=self.login_registro_var.get(),
                senha=self.senha_registro_var.get(),
                email=self.email_var.get(),
                nome=self.nome_var.get(),
                idade=idade,
            )
        except (UsuarioErro, ValueError) as exc:
            messagebox.showerror("Registro", str(exc))
            return
        messagebox.showinfo("Registro", f"Usuario {usuario.login} criado.")

    # ---------------------------------------------------------- notes logic

    def _refresh_notes(self) -> None:
        if not self.current_user:
            return
        self.notes_list.delete(0, tk.END)
        self.index_to_note.clear()
        notes = self.note_service.list_notes(self.current_user.login)
        for idx, note in enumerate(notes):
            self.notes_list.insert(idx, f"{note.title} ({note.updated_at:%H:%M})")
            self.index_to_note[idx] = note.note_id
        self.history_box.delete(0, tk.END)
        self.attachments_list.delete(0, tk.END)
        if self.current_note_id and not self.note_service.get_note(self.current_note_id):
            self.current_note_id = None
        if self.current_note_id:
            self._load_note(self.current_note_id)

    def _select_note(self, _event) -> None:
        selection = self.notes_list.curselection()
        if not selection:
            return
        idx = selection[0]
        note_id = self.index_to_note.get(idx)
        if note_id:
            self._load_note(note_id)

    def _load_note(self, note_id: str) -> None:
        note = self.note_service.get_note(note_id)
        if not note:
            return
        self.current_note_id = note.note_id
        self.title_var.set(note.title)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", note.content)
        self.attachments_list.delete(0, tk.END)
        for attach in note.attachments:
            self.attachments_list.insert(tk.END, attach)
        self._load_history(note.note_id)

    def _load_history(self, note_id: str) -> None:
        history = self.sender.history_for(note_id) or []
        self.history_box.delete(0, tk.END)
        for item in history:
            self.history_box.insert(tk.END, item.timestamp.strftime("%d/%m %H:%M"))

    def _new_note(self) -> None:
        self.current_note_id = None
        self.title_var.set("")
        self.content_text.delete("1.0", tk.END)
        self.attachments_list.delete(0, tk.END)
        self.history_box.delete(0, tk.END)

    def _save_note(self) -> None:
        if not self.current_user:
            return
        title = self.title_var.get()
        content = self.content_text.get("1.0", tk.END)
        if self.current_note_id:
            command = self.factory.update_note(self.current_note_id, title, content)
        else:
            command = self.factory.create_note(self.current_user.login, title, content)
        try:
            self.sender.dispatch(command)
        except ValueError as exc:
            messagebox.showerror("Notas", str(exc))
            return
        self._refresh_notes()

    def _attach_file(self) -> None:
        if not self.current_note_id:
            messagebox.showwarning("Anexos", "Selecione uma nota antes de anexar.")
            return
        file_path = filedialog.askopenfilename(title="Selecione um arquivo")
        if not file_path:
            return
        command = self.factory.attach_file(self.current_note_id, file_path)
        try:
            self.sender.dispatch(command)
        except FileNotFoundError:
            messagebox.showerror("Anexos", "Arquivo nao encontrado.")
            return
        self._refresh_notes()

    def _delete_note(self) -> None:
        if not self.current_note_id:
            return
        if not messagebox.askyesno("Excluir", "Deseja remover esta nota?"):
            return
        command = self.factory.delete_note(self.current_note_id)
        self.sender.dispatch(command)
        self._new_note()
        self._refresh_notes()

    def _undo(self) -> None:
        result = self.sender.undo_last()
        if not result:
            messagebox.showinfo("Desfazer", "Nao ha operacoes para desfazer.")
            return
        self._refresh_notes()

    # ================================================================== shapefile

    def _build_shapefile_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)

        # ── Título ───────────────────────────────────────────────────────
        tk.Label(
            panel, text="Visualização de Shapefile",
            bg=_APP_BG, fg="#f5f5f5", font=("Helvetica", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # ── Barra de controles ───────────────────────────────────────────
        ctrl = tk.Frame(panel, bg=_APP_BG)
        ctrl.pack(fill="x", padx=16, pady=(0, 6))

        for text, cmd in [
            ("Selecionar Arquivo", self._select_shapefile),
            ("Carregar Camada", self._render_shapefile),
            ("Limpar Mapa", self._clear_shapefile),
        ]:
            tk.Button(
                ctrl, text=text,
                bg=_SIDEBAR_BTN_BG, fg=_SIDEBAR_FG,
                activebackground=_SIDEBAR_BTN_HOVER, activeforeground=_SIDEBAR_FG,
                relief="flat", font=("Helvetica", 10), padx=12, pady=6,
                cursor="hand2", command=cmd,
            ).pack(side="left", padx=(0, 6))

        self._shp_tile_mode = tk.StringVar(value="satellite")
        tk.Button(
            ctrl, text="Satélite / Rua",
            bg="#1a3a5c", fg=_SIDEBAR_FG,
            activebackground="#245080", activeforeground=_SIDEBAR_FG,
            relief="flat", font=("Helvetica", 10), padx=12, pady=6,
            cursor="hand2", command=self._toggle_tile_server,
        ).pack(side="left", padx=(0, 16))

        self._shp_filename_var = tk.StringVar(value="Nenhum arquivo selecionado")
        tk.Label(
            ctrl, textvariable=self._shp_filename_var,
            bg=_APP_BG, fg=_ACCENT, font=("Helvetica", 10, "italic"),
        ).pack(side="left")

        # ── Mapa interativo ──────────────────────────────────────────────
        try:
            import tkintermapview
            self._map_widget = tkintermapview.TkinterMapView(panel, corner_radius=0)
            self._map_widget.pack(fill="both", expand=True, padx=16, pady=(0, 4))
            # Tile de satélite Google como base — alinhado com RF01
            self._map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22,
            )
            # Centro padrão: Paraíba, Brasil
            self._map_widget.set_position(-7.12, -36.72)
            self._map_widget.set_zoom(7)
            self._map_available = True
        except ImportError:
            tk.Label(
                panel,
                text="Instale 'tkintermapview' e 'geopandas' para usar este painel.",
                bg=_APP_BG, fg="#ff6666", font=("Helvetica", 12),
            ).pack(expand=True)
            self._map_available = False

        # ── Status ───────────────────────────────────────────────────────
        self._shp_status_var = tk.StringVar(value="")
        tk.Label(
            panel, textvariable=self._shp_status_var,
            bg=_APP_BG, fg=_ACCENT, font=("Helvetica", 10),
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self._shp_selected_path: Optional[str] = None
        self._shp_drawn_shapes: list = []
        return panel

    def _select_shapefile(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o Shapefile",
            filetypes=[
                ("Shapefile", "*.shp"),
                ("ZIP com Shapefile", "*.zip"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not path:
            return
        self._shp_selected_path = path
        self._shp_filename_var.set(path.replace("\\", "/").split("/")[-1])
        self._shp_status_var.set("")

    def _render_shapefile(self) -> None:
        if not getattr(self, "_map_available", False):
            messagebox.showerror("Shapefile", "Mapa não disponível. Verifique as dependências.")
            return
        if not self._shp_selected_path:
            messagebox.showwarning("Shapefile", "Selecione um arquivo antes de carregar.")
            return

        try:
            import geopandas as gpd
        except ImportError:
            messagebox.showerror("Shapefile", "Instale 'geopandas' para renderizar shapefiles.")
            return

        self._shp_status_var.set("Lendo arquivo...")
        self.root.update()

        try:
            path = self._shp_selected_path
            gdf = (
                gpd.read_file(f"zip://{path}")
                if path.lower().endswith(".zip")
                else gpd.read_file(path)
            )
        except Exception as exc:
            messagebox.showerror("Shapefile", f"Erro ao ler arquivo:\n{exc}")
            self._shp_status_var.set("")
            return

        crs_info = "sem CRS"
        if gdf.crs is None:
            self._shp_status_var.set("Aviso: arquivo sem CRS definido — assumindo WGS84.")
        elif gdf.crs.to_epsg() != 4326:
            crs_info = gdf.crs.to_string()
            self._shp_status_var.set(f"Reprojetando {crs_info} → WGS84...")
            self.root.update()
            gdf = gdf.to_crs(epsg=4326)
        else:
            crs_info = "EPSG:4326"

        self._clear_shapefile()
        self._shp_status_var.set("Renderizando camadas...")
        self.root.update()

        count = 0
        for geom in gdf.geometry:
            if geom is None:
                continue
            self._shp_drawn_shapes.extend(self._draw_geometry(geom))
            count += 1

        # Centralizar e dar zoom no extent da camada
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        self._map_widget.set_position(center_lat, center_lon)
        self._map_widget.set_zoom(self._span_to_zoom(
            max(bounds[3] - bounds[1], bounds[2] - bounds[0])
        ))

        feat = "feição" if count == 1 else "feições"
        self._shp_status_var.set(
            f"{count} {feat} renderizada(s)  |  CRS original: {crs_info}"
        )

    def _draw_geometry(self, geom) -> list:
        """Converte uma geometria shapely em objetos do mapa e retorna a lista."""
        shapes = []
        t = geom.geom_type

        if t == "Polygon":
            coords = [(y, x) for x, y in geom.exterior.coords]
            shapes.append(self._map_widget.set_polygon(
                coords, fill_color=None, outline_color="#7ec850", border_width=2,
            ))

        elif t == "MultiPolygon":
            for poly in geom.geoms:
                shapes.extend(self._draw_geometry(poly))

        elif t == "LineString":
            coords = [(y, x) for x, y in geom.coords]
            shapes.append(self._map_widget.set_path(coords, color="#4da6ff", width=2))

        elif t == "MultiLineString":
            for line in geom.geoms:
                shapes.extend(self._draw_geometry(line))

        elif t == "Point":
            shapes.append(self._map_widget.set_marker(geom.y, geom.x, text=""))

        elif t == "MultiPoint":
            for pt in geom.geoms:
                shapes.extend(self._draw_geometry(pt))

        elif t == "GeometryCollection":
            for g in geom.geoms:
                shapes.extend(self._draw_geometry(g))

        return shapes

    def _clear_shapefile(self) -> None:
        for shape in self._shp_drawn_shapes:
            try:
                shape.delete()
            except Exception:
                pass
        self._shp_drawn_shapes.clear()
        self._shp_status_var.set("")

    def _toggle_tile_server(self) -> None:
        if not getattr(self, "_map_available", False):
            return
        import tkintermapview
        if self._shp_tile_mode.get() == "satellite":
            self._map_widget.set_tile_server(
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
            )
            self._shp_tile_mode.set("street")
        else:
            self._map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=s&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22,
            )
            self._shp_tile_mode.set("satellite")

    @staticmethod
    def _span_to_zoom(span: float) -> int:
        """Converte extensão geográfica (graus) em nível de zoom aproximado."""
        thresholds = [
            (40, 4), (20, 5), (10, 6), (5, 7),
            (2, 8), (1, 9), (0.5, 10), (0.1, 12),
            (0.05, 13),
        ]
        for limit, zoom in thresholds:
            if span > limit:
                return zoom
        return 14

    # ================================================================== satélite

    def _build_satellite_panel(self) -> tk.Frame:
        panel = tk.Frame(self.content_area, bg=_APP_BG)

        # ── Título ──────────────────────────────────────────────────────
        tk.Label(
            panel, text="Análise de Satélite Sentinel-2",
            bg=_APP_BG, fg="#f5f5f5", font=("Helvetica", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # ── Credenciais ─────────────────────────────────────────────────
        cred_frame = tk.LabelFrame(
            panel, text="Credenciais Copernicus", bg=_APP_BG, fg="#aaaaaa",
            font=("Helvetica", 9),
        )
        cred_frame.pack(fill="x", padx=16, pady=(0, 8))

        self._sat_user_var = tk.StringVar()
        self._sat_pass_var = tk.StringVar()

        tk.Label(cred_frame, text="Usuário", bg=_APP_BG, fg="#f5f5f5",
                 font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        tk.Entry(cred_frame, textvariable=self._sat_user_var, width=24,
                 bg="#1c1c1c", fg="#f5f5f5", insertbackground="#f5f5f5").grid(
            row=0, column=1, padx=8, pady=4)

        tk.Label(cred_frame, text="Senha", bg=_APP_BG, fg="#f5f5f5",
                 font=("Helvetica", 10)).grid(row=0, column=2, sticky="w", padx=8)
        tk.Entry(cred_frame, textvariable=self._sat_pass_var, show="*", width=24,
                 bg="#1c1c1c", fg="#f5f5f5", insertbackground="#f5f5f5").grid(
            row=0, column=3, padx=8, pady=4)

        tk.Button(
            cred_frame, text="Autenticar",
            bg=_SIDEBAR_BTN_BG, fg=_SIDEBAR_FG,
            activebackground=_SIDEBAR_BTN_HOVER, activeforeground=_SIDEBAR_FG,
            relief="flat", font=("Helvetica", 10), padx=10, pady=4,
            cursor="hand2", command=self._sat_authenticate,
        ).grid(row=0, column=4, padx=12, pady=4)

        self._sat_auth_label = tk.Label(
            cred_frame, text="Não autenticado", bg=_APP_BG,
            fg="#ff6666", font=("Helvetica", 9, "italic"),
        )
        self._sat_auth_label.grid(row=0, column=5, padx=8)

        # ── Parâmetros de busca ─────────────────────────────────────────
        params_frame = tk.Frame(panel, bg=_APP_BG)
        params_frame.pack(fill="x", padx=16, pady=(0, 8))

        bbox_frame = tk.LabelFrame(
            params_frame, text="Bounding Box (WGS84)", bg=_APP_BG, fg="#aaaaaa",
            font=("Helvetica", 9),
        )
        bbox_frame.pack(side="left", padx=(0, 12))

        self._sat_lat_min = tk.StringVar(value="-8.0")
        self._sat_lat_max = tk.StringVar(value="-7.0")
        self._sat_lon_min = tk.StringVar(value="-35.5")
        self._sat_lon_max = tk.StringVar(value="-34.5")

        for i, (lbl, var) in enumerate([
            ("Lat mín", self._sat_lat_min), ("Lat máx", self._sat_lat_max),
            ("Lon mín", self._sat_lon_min), ("Lon máx", self._sat_lon_max),
        ]):
            tk.Label(bbox_frame, text=lbl, bg=_APP_BG, fg="#f5f5f5",
                     font=("Helvetica", 9)).grid(row=i, column=0, sticky="w", padx=6, pady=2)
            tk.Entry(bbox_frame, textvariable=var, width=10,
                     bg="#1c1c1c", fg="#f5f5f5", insertbackground="#f5f5f5").grid(
                row=i, column=1, padx=6, pady=2)

        period_frame = tk.LabelFrame(
            params_frame, text="Período e Filtros", bg=_APP_BG, fg="#aaaaaa",
            font=("Helvetica", 9),
        )
        period_frame.pack(side="left")

        self._sat_start_var = tk.StringVar(value="2024-01-01")
        self._sat_end_var = tk.StringVar(value="2024-12-31")
        self._sat_cloud_var = tk.StringVar(value="30")
        self._sat_threshold_var = tk.StringVar(value="0.3")
        self._sat_index_var = tk.StringVar(value="ndvi")

        for i, (lbl, var) in enumerate([
            ("Início (AAAA-MM-DD)", self._sat_start_var),
            ("Fim (AAAA-MM-DD)", self._sat_end_var),
            ("Nuvens máx (%)", self._sat_cloud_var),
            ("Limiar NDVI", self._sat_threshold_var),
        ]):
            tk.Label(period_frame, text=lbl, bg=_APP_BG, fg="#f5f5f5",
                     font=("Helvetica", 9)).grid(row=i, column=0, sticky="w", padx=6, pady=2)
            tk.Entry(period_frame, textvariable=var, width=16,
                     bg="#1c1c1c", fg="#f5f5f5", insertbackground="#f5f5f5").grid(
                row=i, column=1, padx=6, pady=2)

        tk.Label(period_frame, text="Índice", bg=_APP_BG, fg="#f5f5f5",
                 font=("Helvetica", 9)).grid(row=4, column=0, sticky="w", padx=6, pady=2)
        ttk.Combobox(
            period_frame, textvariable=self._sat_index_var,
            values=["ndvi", "evi"], state="readonly", width=8,
        ).grid(row=4, column=1, padx=6, pady=2)

        # ── Botões de ação ──────────────────────────────────────────────
        actions_frame = tk.Frame(panel, bg=_APP_BG)
        actions_frame.pack(fill="x", padx=16, pady=(0, 8))

        for text, cmd in [
            ("Buscar Imagens", self._sat_search),
            ("Processar NDVI/EVI", self._sat_process),
            ("Detectar Anomalias", self._sat_detect),
        ]:
            tk.Button(
                actions_frame, text=text,
                bg=_SIDEBAR_BTN_BG, fg=_SIDEBAR_FG,
                activebackground=_SIDEBAR_BTN_HOVER, activeforeground=_SIDEBAR_FG,
                relief="flat", font=("Helvetica", 10), padx=14, pady=6,
                cursor="hand2", command=cmd,
            ).pack(side="left", padx=(0, 8))

        # ── Área central: lista de imagens + visualização ───────────────
        center_frame = tk.Frame(panel, bg=_APP_BG)
        center_frame.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        # Lista de imagens encontradas
        left_col = tk.Frame(center_frame, bg=_APP_BG)
        left_col.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(left_col, text="Imagens disponíveis:", bg=_APP_BG, fg="#aaaaaa",
                 font=("Helvetica", 9)).pack(anchor="w")

        images_scroll = ttk.Scrollbar(left_col, orient="vertical")
        self._sat_images_list = tk.Listbox(
            left_col, width=52, height=8,
            bg="#1c1c1c", fg="#f5f5f5", selectbackground=_SIDEBAR_BTN_BG,
            yscrollcommand=images_scroll.set,
        )
        images_scroll.config(command=self._sat_images_list.yview)
        self._sat_images_list.pack(side="left", fill="y")
        images_scroll.pack(side="left", fill="y")

        # Anomalias
        right_col = tk.Frame(center_frame, bg=_APP_BG)
        right_col.pack(side="left", fill="both", expand=True)

        tk.Label(right_col, text="Anomalias detectadas:", bg=_APP_BG, fg="#aaaaaa",
                 font=("Helvetica", 9)).pack(anchor="w")

        anom_scroll = ttk.Scrollbar(right_col, orient="vertical")
        self._sat_anomalies_list = tk.Listbox(
            right_col, bg="#1c1c1c", fg="#f5f5f5",
            selectbackground=_SIDEBAR_BTN_BG,
            yscrollcommand=anom_scroll.set,
        )
        anom_scroll.config(command=self._sat_anomalies_list.yview)
        self._sat_anomalies_list.pack(side="left", fill="both", expand=True)
        anom_scroll.pack(side="left", fill="y")

        # ── Visualização NDVI ───────────────────────────────────────────
        ndvi_frame = tk.Frame(panel, bg=_APP_BG)
        ndvi_frame.pack(fill="x", padx=16, pady=(4, 0))

        tk.Label(ndvi_frame, text="Visualização NDVI:", bg=_APP_BG, fg="#aaaaaa",
                 font=("Helvetica", 9)).pack(anchor="w")

        self._ndvi_canvas = tk.Label(
            ndvi_frame, bg="#1c1c1c", width=80, height=8,
            text="Processe uma imagem para visualizar o NDVI",
            fg="#555555", font=("Helvetica", 10),
        )
        self._ndvi_canvas.pack(fill="x")
        self._ndvi_photo = None  # mantém referência para evitar GC

        # ── Status ──────────────────────────────────────────────────────
        self._sat_status_var = tk.StringVar(value="")
        tk.Label(
            panel, textvariable=self._sat_status_var,
            bg=_APP_BG, fg=_ACCENT, font=("Helvetica", 10),
        ).pack(anchor="w", padx=16, pady=(4, 8))

        self._sat_found_images: list = []
        self._sat_current_result = None
        return panel

    # ------------------------------------------------------------------ handlers satélite

    def _sat_authenticate(self) -> None:
        if not self.satellite_service:
            messagebox.showerror("Satélite", "SatelliteService não inicializado.")
            return
        user = self._sat_user_var.get().strip()
        password = self._sat_pass_var.get().strip()
        if not user or not password:
            messagebox.showwarning("Autenticação", "Informe usuário e senha.")
            return
        self._sat_status_var.set("Autenticando...")
        self.root.update()
        try:
            self.satellite_service.configure_credentials(user, password)
            self._sat_auth_label.config(text="Autenticado", fg=_ACCENT)
            self._sat_status_var.set("Autenticação realizada com sucesso.")
        except Exception as exc:
            self._sat_auth_label.config(text="Falha", fg="#ff6666")
            messagebox.showerror("Autenticação", str(exc))
            self._sat_status_var.set("")

    def _sat_search(self) -> None:
        if not self.satellite_service:
            messagebox.showerror("Satélite", "SatelliteService não inicializado.")
            return
        try:
            from app.models.satellite import BoundingBox
            bbox = BoundingBox(
                min_lat=float(self._sat_lat_min.get()),
                min_lon=float(self._sat_lon_min.get()),
                max_lat=float(self._sat_lat_max.get()),
                max_lon=float(self._sat_lon_max.get()),
            )
            from datetime import datetime
            start = datetime.strptime(self._sat_start_var.get().strip(), "%Y-%m-%d")
            end = datetime.strptime(self._sat_end_var.get().strip(), "%Y-%m-%d")
            cloud = float(self._sat_cloud_var.get())
        except ValueError as exc:
            messagebox.showerror("Parâmetros", f"Valor inválido: {exc}")
            return

        self._sat_status_var.set("Buscando imagens...")
        self.root.update()
        try:
            images = self.satellite_service.search_images(bbox, start, end, cloud)
        except RuntimeError as exc:
            messagebox.showerror("Busca", str(exc))
            self._sat_status_var.set("")
            return

        self._sat_found_images = images
        self._sat_images_list.delete(0, tk.END)
        for img in images:
            self._sat_images_list.insert(tk.END, img.label())

        self._sat_status_var.set(
            f"{len(images)} imagem(s) encontrada(s)." if images
            else "Nenhuma imagem encontrada para os parâmetros informados."
        )

    def _sat_process(self) -> None:
        if not self.satellite_service:
            messagebox.showerror("Satélite", "SatelliteService não inicializado.")
            return
        selection = self._sat_images_list.curselection()
        if not selection:
            messagebox.showwarning("Processar", "Selecione uma imagem na lista.")
            return

        image = self._sat_found_images[selection[0]]
        index = self._sat_index_var.get()
        self._sat_status_var.set(
            f"Baixando bandas e calculando {index.upper()}... (pode demorar)"
        )
        self.root.update()
        try:
            result = self.satellite_service.process_image(image.image_id, index)
        except RuntimeError as exc:
            messagebox.showerror("Processamento", str(exc))
            self._sat_status_var.set("")
            return

        self._sat_current_result = result
        self._render_ndvi_image(result)
        self._sat_status_var.set(
            f"{index.upper()} calculado — média={result.mean_value:.3f}  "
            f"min={result.min_value:.3f}  max={result.max_value:.3f}"
        )

    def _sat_detect(self) -> None:
        if not self.satellite_service:
            messagebox.showerror("Satélite", "SatelliteService não inicializado.")
            return
        if not self._sat_current_result:
            messagebox.showwarning("Anomalias", "Processe uma imagem primeiro.")
            return
        try:
            threshold = float(self._sat_threshold_var.get())
        except ValueError:
            messagebox.showerror("Parâmetros", "Limiar NDVI inválido.")
            return

        self._sat_status_var.set("Detectando anomalias...")
        self.root.update()
        try:
            anomalies = self.satellite_service.detect_anomalies(
                self._sat_current_result, threshold
            )
        except Exception as exc:
            messagebox.showerror("Anomalias", str(exc))
            self._sat_status_var.set("")
            return

        self._sat_anomalies_list.delete(0, tk.END)
        for anomaly in anomalies:
            self._sat_anomalies_list.insert(tk.END, anomaly.label())

        self._sat_status_var.set(
            f"{len(anomalies)} anomalia(s) detectada(s) com NDVI < {threshold}."
        )

    def _render_ndvi_image(self, result) -> None:
        """Renderiza o array NDVI como imagem colorida no painel."""
        try:
            from PIL import ImageTk
            from app.utils.ndvi_calculator import NDVICalculator
            pil_img = NDVICalculator.to_image(result, width=860, height=120)
            self._ndvi_photo = ImageTk.PhotoImage(pil_img)
            self._ndvi_canvas.config(
                image=self._ndvi_photo, text="", width=860, height=120
            )
        except ImportError:
            self._ndvi_canvas.config(
                text="Instale Pillow para visualizar o NDVI",
                fg="#ff6666",
            )

    # ================================================================== fim

    def run(self) -> None:
        self.root.mainloop()
