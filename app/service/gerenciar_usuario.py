from typing import List

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
from app.utils.cache import CacheRAM


# =============================================================================
# <<Service>> GerenciarUsuarioService
# Responsável pelas operações CRUD e administrativas sobre Usuários.
# Utiliza cache em RAM para acesso rápido aos dados.
# =============================================================================
class GerenciarUsuarioService:
    """
    <<Service>> GerenciarUsuarioService
    Gerencia o ciclo de vida dos usuários: listagem, cadastro, edição,
    desativação, exclusão e alteração de permissões.
    
    **Cache em RAM**: Usa CacheRAM para armazenar dados em memória.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        # Inicializa cache com dados do BD
        if not CacheRAM._inicializado:
            usuarios = self._db.query(UsuarioORM).all()
            CacheRAM.inicializar(usuarios)

    # ------------------------------------------------------------------
    # mostrarLista()
    # ------------------------------------------------------------------
    def mostrar_lista(self, somente_ativos: bool = True) -> List[UsuarioORM]:
        """Retorna a lista de usuários do cache RAM (rápido)."""
        return CacheRAM.listar_todos(somente_ativos)

    def buscar_por_id(self, usuario_id: int) -> UsuarioORM:
        """Busca um usuário pelo ID ou lança 404."""
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
        """Cadastra um novo usuário (admin pode definir is_admin)."""
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
            is_admin=is_admin,
        )
        self._db.add(novo)
        self._db.commit()
        self._db.refresh(novo)
        # Adiciona ao cache RAM
        CacheRAM.adicionar(novo)
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
        # Atualiza cache RAM
        CacheRAM.atualizar(usuario)
        return usuario

    # ------------------------------------------------------------------
    # Deletar / Desativar
    # ------------------------------------------------------------------
    def deletar(self, usuario_id: int) -> None:
        """Remove permanentemente um usuário (uso administrativo)."""
        usuario = self.buscar_por_id(usuario_id)
        self._db.delete(usuario)
        self._db.commit()
        # Remove do cache RAM
        CacheRAM.remover(usuario.id)

    def desativar(self, usuario_id: int) -> UsuarioORM:
        """Desativa (soft delete) a conta de um usuário."""
        usuario = self.buscar_por_id(usuario_id)
        usuario.desativar()
        self._db.commit()
        self._db.refresh(usuario)
        # Atualiza cache RAM
        CacheRAM.atualizar(usuario)
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
        # Atualiza cache RAM
        CacheRAM.atualizar(usuario)
        return usuario

    def visualizar_todos_usuarios(self) -> List[UsuarioORM]:
        """Retorna TODOS os usuários do cache RAM, inclusive inativos."""
        todos = CacheRAM.listar_todos(somente_ativos=False)
        return AdministradorMixin.visualizar_todos_usuarios(todos)
    
    def obter_estatisticas_cache(self) -> dict:
        """Retorna estatísticas do cache RAM (demonstração)."""
        total_bd = self._db.query(UsuarioORM).count()
        return CacheRAM.obter_estatisticas(total_bd)
