from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from app.models.usuario import UsuarioErro
from app.patterns.command import (
    AttachContentCommand,
    CreateNoteCommand,
    DeleteNoteCommand,
    UpdateNoteCommand,
)


class RegisterPayload(BaseModel):
    login: str
    senha: str
    email: str
    nome: str
    idade: int


class CredentialsPayload(BaseModel):
    login: str
    senha: str


class NotePayload(CredentialsPayload):
    title: str
    content: str


class NoteUpdatePayload(CredentialsPayload):
    title: str
    content: str


def create_api_app(sender, receiver, note_service, user_service) -> FastAPI:
    app = FastAPI(
        title="Notes App API",
        description="Interface REST com Swagger para o Notes App",
        version="2.0.0",
    )

    security = HTTPBasic()

    def _auth(login: str, senha: str):
        try:
            return user_service.autenticar(login, senha)
        except UsuarioErro as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def _require_note(note_id: str, owner: str):
        note = note_service.get_note(note_id)
        if not note or note.owner != owner:
            raise HTTPException(status_code=404, detail="Nota nao encontrada para o usuario informado.")
        return note

    @app.post("/register", tags=["Auth"])
    def register(payload: RegisterPayload):
        try:
            user_service.registrar(
                login=payload.login,
                senha=payload.senha,
                email=payload.email,
                nome=payload.nome,
                idade=payload.idade,
            )
        except UsuarioErro as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"message": "Usuario criado com sucesso."}

    @app.post("/login", tags=["Auth"])
    def login(payload: CredentialsPayload):
        _auth(payload.login, payload.senha)
        return {"message": "Login valido."}

    @app.get("/notes", tags=["Notes"])
    def list_notes(credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        notes = note_service.list_notes(usuario.login)
        return [note.to_dict() for note in notes]

    @app.post("/notes", tags=["Notes"])
    def create_note(payload: NotePayload):
        usuario = _auth(payload.login, payload.senha)
        command = CreateNoteCommand(receiver, usuario.login, payload.title, payload.content)
        note = sender.dispatch(command)
        return {"message": "Nota criada.", "note_id": note.note_id}

    @app.put("/notes/{note_id}", tags=["Notes"])
    def update_note(note_id: str, payload: NoteUpdatePayload):
        usuario = _auth(payload.login, payload.senha)
        _require_note(note_id, usuario.login)
        command = UpdateNoteCommand(receiver, note_id, payload.title, payload.content)
        try:
            note = sender.dispatch(command)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"message": "Nota atualizada.", "note": note.to_dict()}

    @app.delete("/notes/{note_id}", tags=["Notes"])
    def delete_note(note_id: str, credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        _require_note(note_id, usuario.login)
        command = DeleteNoteCommand(receiver, note_id)
        try:
            sender.dispatch(command)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"message": "Nota removida."}

    @app.post("/notes/{note_id}/attachments", tags=["Notes"])
    async def upload_attachment(
        note_id: str,
        login: str = Form(...),
        senha: str = Form(...),
        arquivo: UploadFile = File(...),
    ):
        usuario = _auth(login, senha)
        _require_note(note_id, usuario.login)
        payload = await arquivo.read()
        command = AttachContentCommand(receiver, note_id, arquivo.filename or "attachment", payload)
        try:
            note = sender.dispatch(command)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (IOError, OSError) as exc:
            raise HTTPException(status_code=500, detail="Erro ao salvar arquivo no servidor.") from exc
        return {
            "message": "Arquivo anexado.",
            "attachments": note.attachments,
            "note_id": note.note_id,
        }

    @app.get("/notes/{note_id}/history", tags=["History"])
    def note_history(note_id: str, credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        _require_note(note_id, usuario.login)
        history = sender.history_for(note_id) or []
        return [
            {"timestamp": item.timestamp.isoformat(), "state": item.state}
            for item in history
        ]

    @app.post("/commands/undo", tags=["History"])
    def undo_command(credentials: HTTPBasicCredentials = Depends(security)):
        _auth(credentials.username, credentials.password)
        if not sender.undo_last():
            raise HTTPException(status_code=400, detail="Nao ha operacoes para desfazer.")
        return {"message": "Ultima operacao desfeita."}

    return app
