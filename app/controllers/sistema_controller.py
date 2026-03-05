from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_senha
from app.models.usuario import (
    AdministradorMixin,
    AlterarPermissaoSchema,
    UsuarioCriar,
    UsuarioAtualizar,
    UsuarioORM,
)


# =============================================================================
# <<Control>> ControleSistema
# =============================================================================
class ControleSistema:
    """
    Controla operações centrais sobre Usuários.
    Expõe: mostrarLista(), Edicao(), Cadastro().
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # mostrarLista()
    # ------------------------------------------------------------------
    def mostrar_lista(self, somente_ativos: bool = True) -> List[UsuarioORM]:
        """Retorna a lista de usuários (padrão: apenas ativos)."""
        query = self._db.query(UsuarioORM)
        if somente_ativos:
            query = query.filter(UsuarioORM.ativo == True)
        return query.all()

    def buscar_por_id(self, usuario_id: int) -> UsuarioORM:
        usuario = self._db.query(UsuarioORM).filter(UsuarioORM.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {usuario_id} não encontrado.",
            )
        return usuario

    # ------------------------------------------------------------------
    # Cadastro()
    # ------------------------------------------------------------------
    def cadastro(self, dados: UsuarioCriar, is_admin: bool = False) -> UsuarioORM:
        """Cadastra um novo usuário."""
        if self._db.query(UsuarioORM).filter(UsuarioORM.email == dados.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado.",
            )
        novo = UsuarioORM(
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            idade=dados.idade,
            is_admin=is_admin,
        )
        self._db.add(novo)
        self._db.commit()
        self._db.refresh(novo)
        return novo

    # ------------------------------------------------------------------
    # Edicao()
    # ------------------------------------------------------------------
    def edicao(self, usuario_id: int, dados: UsuarioAtualizar) -> UsuarioORM:
        """Edita dados de um usuário."""
        usuario = self.buscar_por_id(usuario_id)
        usuario.atualizar_dados(
            nome=dados.nome,
            email=dados.email,
            idade=dados.idade,
        )
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    def deletar(self, usuario_id: int) -> None:
        """Remove permanentemente um usuário (uso administrativo)."""
        usuario = self.buscar_por_id(usuario_id)
        self._db.delete(usuario)
        self._db.commit()

    def desativar(self, usuario_id: int) -> UsuarioORM:
        """Desativa (soft delete) a conta de um usuário."""
        usuario = self.buscar_por_id(usuario_id)
        usuario.desativar()
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    # ------------------------------------------------------------------
    # Operações de Administrador
    # ------------------------------------------------------------------
    def alterar_permissoes(
        self, usuario_id: int, payload: AlterarPermissaoSchema
    ) -> UsuarioORM:
        """Promove ou rebaixa um usuário via AdministradorMixin."""
        usuario = self.buscar_por_id(usuario_id)
        AdministradorMixin.alterar_permissoes(usuario, payload.is_admin)
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    def visualizar_todos_usuarios(self) -> List[UsuarioORM]:
        """Retorna TODOS os usuários, inclusive inativos (uso do admin)."""
        todos = self._db.query(UsuarioORM).all()
        return AdministradorMixin.visualizar_todos_usuarios(todos)
