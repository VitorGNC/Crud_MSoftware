"""
<<Boundary>> AlterarInfos
Rotas do usuário autenticado sobre si mesmo:
  - Login()                →  POST /login/login
  - SolicitarEdicao()      →  PUT  /login/perfil
  - SolicitarEncerramento()→  DELETE /login/perfil
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import get_usuario_atual
from app.database import get_db
from app.service.facade_service import FacadeService
from app.models.usuario import (
    UsuarioCriar,
    UsuarioAtualizar,
    UsuarioResposta,
    UsuarioORM,
)

router = APIRouter(tags=["AlterarInfos (Usuário)"])

# ------------------------------------------------------------------
# Login()
# ------------------------------------------------------------------
@router.post("/login", summary="Login – obtém token JWT")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return FacadeService.get_instance(db).autenticar(form)


# ------------------------------------------------------------------
# Cadastro público (auto-registro)
# ------------------------------------------------------------------
@router.post(
    "/login/registrar",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Registro público de novo usuário",
)
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    return FacadeService.get_instance(db).registrar(dados)


# ------------------------------------------------------------------
# GET /login/perfil  –  perfil próprio
# ------------------------------------------------------------------
@router.get(
    "/login/perfil",
    response_model=UsuarioResposta,
    summary="Ver perfil próprio",
)
def ver_perfil(usuario: UsuarioORM = Depends(get_usuario_atual)):
    return usuario


# ------------------------------------------------------------------
# SolicitarEdicao()  –  editar dados próprios
# ------------------------------------------------------------------
@router.put(
    "/login/perfil",
    response_model=UsuarioResposta,
    summary="Editar dados próprios",
)
def solicitar_edicao(
    dados: UsuarioAtualizar,
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return FacadeService.get_instance(db).editar_perfil(usuario.id, dados)


# ------------------------------------------------------------------
# SolicitarEncerramento()  –  desativar conta própria
# ------------------------------------------------------------------
@router.delete(
    "/login/perfil",
    response_model=UsuarioResposta,
    summary="Encerrar conta própria (desativar)",
)
def solicitar_encerramento(
    usuario: UsuarioORM = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
):
    return FacadeService.get_instance(db).encerrar_conta(usuario.id)
