"""
<<Boundary>> AlterarInfos
Rotas do usuário autenticado sobre si mesmo:
  - Login()                →  POST /auth/login
  - SolicitarEdicao()      →  PUT  /usuarios/profile
  - SolicitarEncerramento()→  DELETE /usuarios/profile
  - fazerUpload            →  POST /usuarios/profile/medias
  - getMedias              →  GET  /usuarios/profile/medias
  - deleteMedia            →  DELETE /usuarios/profile/medias/{id}
"""
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    criar_access_token,
    get_usuario_atual,
    verificar_senha,
)
from app.database import get_db
from app.controllers.sistema_controller import ControleSistema
from app.controllers.uploader_controller import UploaderController
from app.models.usuario import UsuarioCriar, UsuarioAtualizar, UsuarioResposta, UsuarioORM
from app.models.media import MediaResposta

from datetime import timedelta

router = APIRouter(tags=["AlterarInfos (Usuário)"])


# ------------------------------------------------------------------
# Login()
# ------------------------------------------------------------------
@router.post("/auth/login", summary="Login – obtém token JWT")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario: UsuarioORM = (
        db.query(UsuarioORM)
        .filter(UsuarioORM.email == form.username, UsuarioORM.ativo == True)
        .first()
    )
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")

    token = criar_access_token(
        data={"sub": usuario.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


# ------------------------------------------------------------------
# Cadastro público (auto-registro)
# ------------------------------------------------------------------
@router.post(
    "/usuarios/registrar",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Registro público de novo usuário",
)
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    return ControleSistema(db).cadastro(dados, is_admin=False)


# ------------------------------------------------------------------
# GET /usuarios/profile  –  perfil próprio
# ------------------------------------------------------------------
@router.get(
    "/usuarios/profile",
    response_model=UsuarioResposta,
    summary="Ver perfil próprio",
)
def ver_perfil(usuario: UsuarioORM = Depends(get_usuario_atual)):
    return usuario


# ------------------------------------------------------------------
# SolicitarEdicao()  –  editar dados próprios
# ------------------------------------------------------------------
@router.put(
    "/usuarios/profile",
    response_model=UsuarioResposta,
    summary="Editar dados próprios",
)
def solicitar_edicao(
    dados: UsuarioAtualizar,
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return ControleSistema(db).edicao(usuario.id, dados)


# ------------------------------------------------------------------
# SolicitarEncerramento()  –  desativar conta própria
# ------------------------------------------------------------------
@router.delete(
    "/usuarios/profile",
    response_model=UsuarioResposta,
    summary="Encerrar conta própria (desativar)",
)
def solicitar_encerramento(
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return ControleSistema(db).desativar(usuario.id)


# ==================================================================
# Rotas de Mídia  –  fazerUpload / getMedias / deleteMedia
# ==================================================================

# ------------------------------------------------------------------
# fazerUpload
# ------------------------------------------------------------------
@router.post(
    "/usuarios/profile/medias",
    response_model=MediaResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Fazer upload de mídia",
)
async def fazer_upload(
    file: UploadFile = File(...),
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return await UploaderController(db).upload_media(file, usuario.id)


# ------------------------------------------------------------------
# getMedias
# ------------------------------------------------------------------
@router.get(
    "/usuarios/profile/medias",
    response_model=List[MediaResposta],
    summary="Listar minhas mídias",
)
def get_medias(
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return UploaderController(db).get_medias(usuario.id)


# ------------------------------------------------------------------
# deleteMedia
# ------------------------------------------------------------------
@router.delete(
    "/usuarios/profile/medias/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover mídia própria",
)
def delete_media(
    media_id: int,
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    UploaderController(db).delete_media(media_id, usuario.id, is_admin=False)
