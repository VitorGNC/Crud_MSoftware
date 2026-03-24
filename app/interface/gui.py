from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

from app.models.usuario import UsuarioErro
from app.patterns.command import (
    AttachFileCommand,
    CreateNoteCommand,
    DeleteNoteCommand,
    UpdateNoteCommand,
)
from app.patterns.receiver import NoteReceiver
from app.patterns.sender import CommandSender
from app.services.note_service import NoteService
from app.services.user_service import UserService


class NotesAppGUI:
    def __init__(
        self,
        sender: CommandSender,
        receiver: NoteReceiver,
        note_service: NoteService,
        user_service: UserService,
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.note_service = note_service
        self.user_service = user_service
        self.current_user = None
        self.current_note_id: Optional[str] = None
        self.index_to_note: Dict[int, str] = {}

        self.root = tk.Tk()
        self.root.title("Notes App - Design Patterns")
        self.root.geometry("960x600")
        self.root.configure(bg="#111111")

        self.login_frame = ttk.Frame(self.root, padding=24)
        self.notes_frame = ttk.Frame(self.root, padding=16)

        self._setup_styles()
        self._build_login_frame()
        self._build_notes_frame()
        self._show_login()

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111111")
        style.configure("TLabel", background="#111111", foreground="#f5f5f5")
        style.configure("TButton", padding=8)
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

    def _build_login_frame(self) -> None:
        ttk.Label(self.login_frame, text="Notes App", style="Header.TLabel").grid(
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

        ttk.Label(self.login_frame, text="Senha").grid(
            row=10, column=0, sticky="w"
        )
        
        ttk.Entry(
            self.login_frame, textvariable=self.senha_registro_var, show="*", width=30
        ).grid(row=10, column=1, pady=4)

        ttk.Button(
            self.login_frame, text="Registrar", command=self._handle_register
        ).grid(row=11, column=0, columnspan=2, pady=(12, 0), sticky="ew")

    def _build_notes_frame(self) -> None:
        top_bar = ttk.Frame(self.notes_frame)
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text="Minhas notas", style="Header.TLabel").pack(side="left")

        body = ttk.Frame(self.notes_frame)
        body.pack(fill="both", expand=True, pady=12)

        left = ttk.Frame(body)
        left.pack(side="left", fill="y")
        self.notes_list = tk.Listbox(left, width=32, height=25)
        self.notes_list.pack(side="left", fill="y")
        self.notes_list.bind("<<ListboxSelect>>", self._select_note)
        note_scroll = ttk.Scrollbar(
            left, orient="vertical", command=self.notes_list.yview
        )
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
        ttk.Button(buttons, text="Nova nota", command=self._new_note).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Salvar", command=self._save_note).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Anexar arquivo", command=self._attach_file).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Excluir", command=self._delete_note).pack(
            side="left", padx=4
        )
        ttk.Button(buttons, text="Desfazer", command=self._undo).pack(
            side="left", padx=4
        )

        history_frame = ttk.Frame(right)
        history_frame.pack(fill="both", expand=False)
        ttk.Label(history_frame, text="Historico (memento)").pack(anchor="w")
        self.history_box = tk.Listbox(history_frame, height=5)
        self.history_box.pack(fill="x")

    def _show_login(self) -> None:
        self.notes_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def _show_notes(self) -> None:
        self.login_frame.pack_forget()
        self.notes_frame.pack(fill="both", expand=True)
        self._refresh_notes()

    def _handle_login(self) -> None:
        try:
            usuario = self.user_service.autenticar(
                self.login_var.get(), self.senha_var.get()
            )
        except UsuarioErro as exc:
            messagebox.showerror("Login", str(exc))
            return
        self.current_user = usuario
        self.root.title(f"Notes App - {usuario.login}")
        self._show_notes()

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
        if self.current_note_id and not self.note_service.get_note(
            self.current_note_id
        ):
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
            command = UpdateNoteCommand(
                self.receiver, self.current_note_id, title, content
            )
        else:
            command = CreateNoteCommand(
                self.receiver, self.current_user.login, title, content
            )
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
        command = AttachFileCommand(self.receiver, self.current_note_id, file_path)
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
        command = DeleteNoteCommand(self.receiver, self.current_note_id)
        self.sender.dispatch(command)
        self._new_note()
        self._refresh_notes()

    def _undo(self) -> None:
        result = self.sender.undo_last()
        if not result:
            messagebox.showinfo("Desfazer", "Nao ha operacoes para desfazer.")
            return
        self._refresh_notes()

    def run(self) -> None:
        self.root.mainloop()
