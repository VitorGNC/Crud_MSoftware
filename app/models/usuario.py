from __future__ import annotations

from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, field_validator

from app.database import Base


# =============================================================================
# ORM  –  <<Entity>> Usuário  /  Administrador : Usuário
# =============================================================================
class UsuarioORM(Base):
    """
    <<Entity>> Usuário
    Atributos: nome, senha (hash), email, idade, id
    O campo is_admin diferencia Administrador de Usuário comum.
    """
    __tablename__ = "usuarios"

    id: int         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome: str       = Column(String(100), nullable=False)
    senha_hash: str = Column(String(200), nullable=False)
    email: str      = Column(String(150), unique=True, index=True, nullable=False)
    idade: int      = Column(Integer, nullable=False)
    is_admin: bool  = Column(Boolean, default=False, nullable=False)
    ativo: bool     = Column(Boolean, default=True, nullable=False)

    medias = relationship("MediaORM", back_populates="usuario", cascade="all, delete-orphan")

    # ------------------------------------------------------------------
    # Métodos de negócio  (OOP)
    # ------------------------------------------------------------------
    def atualizar_dados(
        self,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        idade: Optional[int] = None,
    ) -> None:
        """Atualiza os dados próprios do usuário."""
        if nome is not None:
            self.nome = nome
        if email is not None:
            self.email = email
        if idade is not None:
            self.idade = idade

    def desativar(self) -> None:
        """Desativa a conta do usuário (soft delete)."""
        self.ativo = False


class AdministradorMixin:
    """
    Mixin com comportamentos exclusivos do <<Administrador : Usuário>>.
    Aplicado dinamicamente via helper, pois a herança ORM é single-table.
    """

    @staticmethod
    def alterar_permissoes(usuario: UsuarioORM, is_admin: bool) -> None:
        """Promove ou rebaixa um usuário para/de administrador."""
        usuario.is_admin = is_admin

    @staticmethod
    def visualizar_todos_usuarios(db_usuarios: list[UsuarioORM]) -> list[UsuarioORM]:
        """Retorna lista completa de usuários."""
        return db_usuarios


# =============================================================================
# Pydantic Schemas  –  Usuário
# =============================================================================
class UsuarioCriar(BaseModel):
    nome: str
    email: str
    senha: str
    idade: int

    @field_validator("idade")
    @classmethod
    def idade_valida(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError("Idade inválida.")
        return v


class UsuarioAtualizar(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    idade: Optional[int] = None

    @field_validator("idade")
    @classmethod
    def idade_valida(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 150):
            raise ValueError("Idade inválida.")
        return v


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: str
    idade: int
    is_admin: bool
    ativo: bool

    model_config = {"from_attributes": True}


class AlterarPermissaoSchema(BaseModel):
    is_admin: bool
