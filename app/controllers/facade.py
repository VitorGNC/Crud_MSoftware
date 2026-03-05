from __future__ import annotations

from typing import Dict, Optional

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.controllers.gerenciar_usuario import GerenciarUsuarioController
from app.controllers.login_controller import LoginController


# =============================================================================
# <<Facade + Singleton>> FacadeSingletonController
# Ponto único de acesso a GerenciarUsuarioController e LoginController.
# =============================================================================
class FacadeSingletonController:
    """
    <<Facade + Singleton>>

    - Singleton: garante uma única instância por processo; a sessão de banco
      é atualizada a cada chamada a get_instance() para compatibilidade com
      o modelo de sessão por requisição do FastAPI.
    - Facade: expõe uma interface unificada delegando para os dois controllers
      especializados abaixo.

        ┌──────────────────────────────────────────────────┐
        │          FacadeSingletonController               │
        │  ┌─────────────────────┐  ┌───────────────────┐ │
        │  │ GerenciarUsuario    │  │  LoginController  │ │
        │  │ Controller          │  │                   │ │
        │  └─────────────────────┘  └───────────────────┘ │
        └──────────────────────────────────────────────────┘
    """

    _instance: Optional[FacadeSingletonController] = None

    def __new__(cls, db: Session) -> FacadeSingletonController:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        # Atualiza os sub-controllers com a sessão atual da requisição
        cls._instance._db = db
        cls._instance._usuarios = GerenciarUsuarioController(db)
        cls._instance._login = LoginController(db)
        return cls._instance

    @classmethod
    def get_instance(cls, db: Session) -> FacadeSingletonController:
        """Retorna a instância Singleton configurada com a sessão atual."""
        return cls(db)

    # ------------------------------------------------------------------
    # contar_entidades()
    # ------------------------------------------------------------------
    def contar_entidades(self) -> Dict[str, int]:
        """Retorna a quantidade de entidades cadastradas no sistema."""
        from app.models.usuario import UsuarioORM
        from app.models.media import MediaORM

        n_usuarios = self._db.query(UsuarioORM).count()
        n_medias = self._db.query(MediaORM).count()
        return {
            "usuarios": n_usuarios,
            "medias": n_medias,
            "total": n_usuarios + n_medias,
        }

    # ------------------------------------------------------------------
    # Delegação → GerenciarUsuarioController
    # ------------------------------------------------------------------
    def mostrar_lista(self, somente_ativos: bool = True):
        return self._usuarios.mostrar_lista(somente_ativos)

    def buscar_por_id(self, usuario_id: int):
        return self._usuarios.buscar_por_id(usuario_id)

    def cadastro(self, dados, is_admin: bool = False):
        return self._usuarios.cadastro(dados, is_admin)

    def edicao(self, usuario_id: int, dados):
        return self._usuarios.edicao(usuario_id, dados)

    def deletar(self, usuario_id: int):
        return self._usuarios.deletar(usuario_id)

    def desativar(self, usuario_id: int):
        return self._usuarios.desativar(usuario_id)

    def alterar_permissoes(self, usuario_id: int, payload):
        return self._usuarios.alterar_permissoes(usuario_id, payload)

    def visualizar_todos_usuarios(self):
        return self._usuarios.visualizar_todos_usuarios()

    # ------------------------------------------------------------------
    # Delegação → LoginController
    # ------------------------------------------------------------------
    def autenticar(self, form: OAuth2PasswordRequestForm) -> dict:
        return self._login.autenticar(form)

    def registrar(self, dados):
        return self._login.registrar(dados)

    def editar_perfil(self, usuario_id: int, dados):
        return self._login.editar_perfil(usuario_id, dados)

    def encerrar_conta(self, usuario_id: int):
        return self._login.encerrar_conta(usuario_id)
