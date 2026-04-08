from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from app.models.satellite import BoundingBox
from app.models.usuario import UsuarioErro
from app.patterns.export import PdfNoteExporter, PlainTextNoteExporter
from app.patterns.factory import CommandFactory
from app.patterns.observer import NoteEventBus


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


class TalhaoPayload(BaseModel):
    nome: str
    variedade_cana: str
    idade: int
    ultima_colheita: str
    solo: str
    status: str
    previsao_colheita: str
    irrigacao: bool


class TalhaoUpdatePayload(BaseModel):
    nome: Optional[str] = None
    variedade_cana: Optional[str] = None
    idade: Optional[int] = None
    ultima_colheita: Optional[str] = None
    solo: Optional[str] = None
    status: Optional[str] = None
    previsao_colheita: Optional[str] = None
    irrigacao: Optional[bool] = None


class SatelliteCredentialsPayload(BaseModel):
    copernicus_user: str
    copernicus_password: str


class SatelliteSearchPayload(BaseModel):
    copernicus_user: str
    copernicus_password: str
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    start_date: str
    end_date: str
    max_cloud: float = 30.0


def create_api_app(sender, receiver, note_service, user_service, talhao_service=None, satellite_service=None) -> FastAPI:
    factory = CommandFactory(receiver)

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
        command = factory.create_note(usuario.login, payload.title, payload.content)
        note = sender.dispatch(command)
        return {"message": "Nota criada.", "note_id": note.note_id}

    @app.put("/notes/{note_id}", tags=["Notes"])
    def update_note(note_id: str, payload: NoteUpdatePayload):
        usuario = _auth(payload.login, payload.senha)
        _require_note(note_id, usuario.login)
        command = factory.update_note(note_id, payload.title, payload.content)
        try:
            note = sender.dispatch(command)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"message": "Nota atualizada.", "note": note.to_dict()}

    @app.delete("/notes/{note_id}", tags=["Notes"])
    def delete_note(note_id: str, credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        _require_note(note_id, usuario.login)
        command = factory.delete_note(note_id)
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
        command = factory.attach_content(note_id, arquivo.filename or "attachment", payload)
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

    @app.get("/notes/{note_id}/export", tags=["Notes"])
    def export_note(
        note_id: str,
        formato: str = Query(default="pdf", pattern="^(pdf|txt)$"),
        credentials: HTTPBasicCredentials = Depends(security),
    ):
        usuario = _auth(credentials.username, credentials.password)
        _require_note(note_id, usuario.login)

        exporter = PdfNoteExporter() if formato == "pdf" else PlainTextNoteExporter()
        media_type = "application/pdf" if formato == "pdf" else "text/plain"
        extension = formato

        try:
            content = note_service.export_note(note_id, exporter)
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="Dependencia 'fpdf2' nao instalada. Execute: pip install fpdf2",
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        filename = f"nota_{note_id[:8]}.{extension}"
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.get("/stats", tags=["Admin"])
    def get_stats(credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        if not usuario.is_admin:
            raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
        return NoteEventBus.get_stats()

    @app.get("/users", tags=["Admin"])
    def list_users(credentials: HTTPBasicCredentials = Depends(security)):
        usuario = _auth(credentials.username, credentials.password)
        if not usuario.is_admin:
            raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
        users = user_service.listar()
        return [u.to_dict() for u in users.values()]

    # ------------------------------------------------------------------ talhoes
    if talhao_service is not None:

        @app.get("/talhoes", tags=["Talhoes"])
        def list_talhoes(credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            return [t.to_dict() for t in talhao_service.listar_talhoes()]

        @app.post("/talhoes", tags=["Talhoes"])
        def create_talhao(payload: TalhaoPayload, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            try:
                talhao = talhao_service.criar_talhao(
                    nome=payload.nome,
                    variedade_cana=payload.variedade_cana,
                    idade=payload.idade,
                    ultima_colheita=payload.ultima_colheita,
                    solo=payload.solo,
                    status=payload.status,
                    previsao_colheita=payload.previsao_colheita,
                    irrigacao=payload.irrigacao,
                )
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            return {"message": "Talhao criado.", "talhao": talhao.to_dict()}

        @app.put("/talhoes/{talhao_id}", tags=["Talhoes"])
        def update_talhao(talhao_id: str, payload: TalhaoUpdatePayload, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            try:
                talhao = talhao_service.atualizar_talhao(
                    talhao_id=talhao_id,
                    nome=payload.nome,
                    variedade_cana=payload.variedade_cana,
                    idade=payload.idade,
                    ultima_colheita=payload.ultima_colheita,
                    solo=payload.solo,
                    status=payload.status,
                    previsao_colheita=payload.previsao_colheita,
                    irrigacao=payload.irrigacao,
                )
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            return {"message": "Talhao atualizado.", "talhao": talhao.to_dict()}

        @app.delete("/talhoes/{talhao_id}", tags=["Talhoes"])
        def delete_talhao(talhao_id: str, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            try:
                talhao_service.remover_talhao(talhao_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            return {"message": "Talhao removido."}

        @app.get("/talhoes/{talhao_id}", tags=["Talhoes"])
        def get_talhao(talhao_id: str, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            talhao = talhao_service.get_talhao(talhao_id)
            if not talhao:
                raise HTTPException(status_code=404, detail="Talhao nao encontrado.")
            return talhao.to_dict()

    # ------------------------------------------------------------------ satelite
    if satellite_service is not None:

        @app.post("/satellite/credentials", tags=["Satelite"])
        def configure_satellite(payload: SatelliteCredentialsPayload, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            try:
                satellite_service.configure_credentials(payload.copernicus_user, payload.copernicus_password)
            except Exception as exc:
                raise HTTPException(status_code=401, detail=f"Falha na autenticacao Copernicus: {exc}") from exc
            return {"message": "Credenciais Copernicus configuradas com sucesso."}

        @app.post("/satellite/search", tags=["Satelite"])
        def search_images(payload: SatelliteSearchPayload, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            try:
                satellite_service.configure_credentials(payload.copernicus_user, payload.copernicus_password)
                bbox = BoundingBox(
                    min_lat=payload.min_lat,
                    min_lon=payload.min_lon,
                    max_lat=payload.max_lat,
                    max_lon=payload.max_lon,
                )
                start = datetime.fromisoformat(payload.start_date)
                end = datetime.fromisoformat(payload.end_date)
                images = satellite_service.search_images(bbox, start, end, payload.max_cloud)
            except RuntimeError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=f"Data invalida: {exc}") from exc
            return [img.to_dict() for img in images]

        @app.get("/satellite/images", tags=["Satelite"])
        def list_images(credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            return [img.to_dict() for img in satellite_service.list_images()]

        @app.post("/satellite/process/{image_id}", tags=["Satelite"])
        def process_image(
            image_id: str,
            index: str = Query(default="ndvi", pattern="^(ndvi|evi)$"),
            credentials: HTTPBasicCredentials = Depends(security),
        ):
            _auth(credentials.username, credentials.password)
            try:
                result = satellite_service.process_image(image_id, index)
            except RuntimeError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            return result.to_dict()

        @app.get("/satellite/result/{image_id}", tags=["Satelite"])
        def get_ndvi_result(image_id: str, credentials: HTTPBasicCredentials = Depends(security)):
            _auth(credentials.username, credentials.password)
            result = satellite_service.get_result(image_id)
            if not result:
                raise HTTPException(status_code=404, detail="Resultado NDVI nao encontrado para esta imagem.")
            return result.to_dict()

        @app.post("/satellite/anomalies/{image_id}", tags=["Satelite"])
        def detect_anomalies(
            image_id: str,
            threshold: float = Query(default=0.3, ge=0.0, le=1.0),
            credentials: HTTPBasicCredentials = Depends(security),
        ):
            _auth(credentials.username, credentials.password)
            result = satellite_service.get_result(image_id)
            if not result:
                raise HTTPException(status_code=404, detail="Resultado NDVI nao encontrado. Execute /satellite/process primeiro.")
            anomalies = satellite_service.detect_anomalies(result, threshold)
            return [a.to_dict() for a in anomalies]

        @app.get("/satellite/anomalies", tags=["Satelite"])
        def list_anomalies(
            image_id: Optional[str] = Query(default=None),
            credentials: HTTPBasicCredentials = Depends(security),
        ):
            _auth(credentials.username, credentials.password)
            return [a.to_dict() for a in satellite_service.list_anomalies(image_id)]

    return app
