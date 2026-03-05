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

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    criar_access_token,
    get_usuario_atual,
    verificar_senha,
)
from app.database import get_db
from app.controllers.usuarios import ControleSistema
from app.models.usuario import (
    UsuarioCriar,
    UsuarioAtualizar,
    UsuarioResposta,
    UsuarioORM,
)

from datetime import timedelta

router = APIRouter(tags=["AlterarInfos (Usuário)"])


# ------------------------------------------------------------------
# Login()
# ------------------------------------------------------------------
@router.post("/login", summary="Login – obtém token JWT")
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

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas."
        )

    token = criar_access_token(
        data={"sub": usuario.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


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
    return ControleSistema(db).cadastro(dados, is_admin=False)


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
    return ControleSistema(db).edicao(usuario.id, dados)


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
    return ControleSistema(db).desativar(usuario.id)
