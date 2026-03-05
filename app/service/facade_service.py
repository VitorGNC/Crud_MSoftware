from __future__ import annotations

from typing import Dict

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.media import MediaORM
from app.models.usuario import UsuarioORM
from app.service.gerenciar_usuario import GerenciarUsuarioService
from app.service.login_controller import LoginController


# =============================================================================
# <<Facade>> FacadeService
# Ponto único de acesso às views para GerenciarUsuarioService e
# LoginController.
#
# Uma nova instância é criada por requisição HTTP, alinhada ao ciclo
# de vida da Session do banco injetada pelo FastAPI via Depends(get_db).
# Usar Singleton aqui seria incorreto: sessões são recursos por-requisição
# e compartilhá-las entre threads concorrentes causaria race conditions.
# =============================================================================
class FacadeService:

    def __init__(self, db: Session) -> None:
        self._db = db
        self._usuarios = GerenciarUsuarioService(db)
        self._login = LoginController(db)

    @classmethod
    def get_instance(cls, db: Session) -> FacadeService:
        """Cria a fachada para a sessão atual da requisição."""
        return cls(db)

    # ------------------------------------------------------------------
    # contar_entidades()
    # ------------------------------------------------------------------
    def contar_entidades(self) -> Dict[str, int]:
        """Retorna a quantidade de entidades cadastradas no sistema."""
        n_usuarios = self._db.query(UsuarioORM).count()
        n_medias = self._db.query(MediaORM).count()
        return {
            "usuarios": n_usuarios,
            "medias": n_medias,
            "total": n_usuarios + n_medias,
        }

    # ------------------------------------------------------------------
    # Delegação → GerenciarUsuarioService
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


# ---------------------------------------------------------------------------
# Alias de compatibilidade — permite migração gradual sem quebrar imports
# existentes. Remova após atualizar todas as views.
# ---------------------------------------------------------------------------
FacadeSingletonService = FacadeService
