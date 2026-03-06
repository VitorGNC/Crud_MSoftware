from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    criar_access_token,
    hash_senha,
    verificar_senha,
)
from app.models.usuario import UsuarioCriar, UsuarioAtualizar, UsuarioORM
from app.utils.cache import CacheRAM


# =============================================================================
# <<Control>> LoginController
# Responsável por autenticação e operações do próprio perfil do usuário.
# Utiliza cache em RAM para acesso rápido aos dados.
# =============================================================================
class LoginController:
    """
    <<Control>> LoginController
    Gerencia login, registro público e edição/encerramento do próprio perfil.
    
    **Cache em RAM**: Usa CacheRAM para armazenar dados em memória.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # autenticar()
    # ------------------------------------------------------------------
    def autenticar(self, form: OAuth2PasswordRequestForm) -> dict:
        """Valida credenciais e retorna o token JWT."""
        usuario: UsuarioORM = (
            self._db.query(UsuarioORM)
            .filter(UsuarioORM.email == form.username, UsuarioORM.ativo == True)
            .first()
        )
        if not usuario or not verificar_senha(form.password, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
            )
        token = criar_access_token(
            data={"sub": str(usuario.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": token, "token_type": "bearer"}

    # ------------------------------------------------------------------
    # registrar()  –  auto-registro público
    # ------------------------------------------------------------------
    def registrar(self, dados: UsuarioCriar) -> UsuarioORM:
        """Cadastro público – sempre cria usuário comum (is_admin=False)."""
        if self._db.query(UsuarioORM).filter(UsuarioORM.email == dados.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado.",
            )
        novo = UsuarioORM(
            login=dados.login,
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            idade=dados.idade,
            is_admin=False,
        )
        self._db.add(novo)
        self._db.commit()
        self._db.refresh(novo)
        # Adiciona ao cache RAM
        CacheRAM.adicionar(novo)
        return novo

    # ------------------------------------------------------------------
    # editar_perfil()
    # ------------------------------------------------------------------
    def editar_perfil(self, usuario_id: int, dados: UsuarioAtualizar) -> UsuarioORM:
        """Edita os dados do próprio perfil."""
        usuario = (
            self._db.query(UsuarioORM).filter(UsuarioORM.id == usuario_id).first()
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        usuario.atualizar_dados(
            nome=dados.nome,
            email=dados.email,
            idade=dados.idade,
        )
        self._db.commit()
        self._db.refresh(usuario)
        # Atualiza cache RAM
        CacheRAM.atualizar(usuario)
        return usuario

    # ------------------------------------------------------------------
    # encerrar_conta()
    # ------------------------------------------------------------------
    def encerrar_conta(self, usuario_id: int) -> UsuarioORM:
        """Desativa (soft delete) o próprio usuário."""
        usuario = (
            self._db.query(UsuarioORM).filter(UsuarioORM.id == usuario_id).first()
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        usuario.desativar()
        self._db.commit()
        self._db.refresh(usuario)
        # Atualiza cache RAM
        CacheRAM.atualizar(usuario)
        return usuario
