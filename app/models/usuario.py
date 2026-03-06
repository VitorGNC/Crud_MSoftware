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
    login: str      = Column(String(12), unique=True, index=True, nullable=False)
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
    login: str
    nome: str
    email: str
    senha: str
    idade: int

    @field_validator("login")
    @classmethod
    def login_valido(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Login não pode ser vazio.")
        if len(v) > 12:
            raise ValueError("Login deve ter no máximo 12 caracteres.")
        if any(c.isdigit() for c in v):
            raise ValueError("Login não pode conter números.")
        return v

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        """
        Política de senha forte (estilo IAM/AWS):
        - Mínimo 8 caracteres
        - Pelo menos 1 letra maiúscula
        - Pelo menos 1 letra minúscula
        - Pelo menos 1 número
        - Pelo menos 1 caractere especial
        """
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres.")
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula.")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número.")
        # Caracteres especiais comuns
        especiais = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        if not any(c in especiais for c in v):
            raise ValueError("Senha deve conter pelo menos um caractere especial (!@#$%^&*).")
        return v

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
    login: str
    nome: str
    email: str
    idade: int
    is_admin: bool
    ativo: bool

    model_config = {"from_attributes": True}


class AlterarPermissaoSchema(BaseModel):
    is_admin: bool
