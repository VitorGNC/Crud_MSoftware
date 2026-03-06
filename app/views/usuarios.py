"""
<<Boundary>> GerenciarUsuários
Rotas exclusivas do Administrador:
  - mostrarLista()     →  GET  /admin/usuarios
  - EdicaoUsuario()    →  PUT  /admin/usuarios/{id}
  - CadastroUsuario()  →  POST /admin/usuarios
  - alterarPermissoes()→  PATCH /admin/usuarios/{id}/permissoes
  - visualizarTodos()  →  GET  /admin/usuarios/todos
  - deletar()          →  DELETE /admin/usuarios/{id}
"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_admin_atual
from app.database import get_db
from app.service.facade_service import FacadeService
from app.models.usuario import (
    AlterarPermissaoSchema,
    UsuarioCriar,
    UsuarioAtualizar,
    UsuarioResposta,
)

router = APIRouter(prefix="/admin", tags=["GerenciarUsuários (Admin)"])


# ------------------------------------------------------------------
# mostrarLista()  –  usuários ativos
# ------------------------------------------------------------------
@router.get(
    "/usuarios",
    response_model=List[UsuarioResposta],
    summary="Listar usuários ativos",
)
def mostrar_lista(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).mostrar_lista(somente_ativos=True)


# ------------------------------------------------------------------
# visualizarTodosUsuarios()  –  inclui inativos
# ------------------------------------------------------------------
@router.get(
    "/usuarios/todos",
    response_model=List[UsuarioResposta],
    summary="Listar TODOS os usuários (admin)",
)
def visualizar_todos_usuarios(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).visualizar_todos_usuarios()


# ------------------------------------------------------------------
# CadastroUsuario()
# ------------------------------------------------------------------
@router.post(
    "/usuarios",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário (admin)",
)
def cadastro_usuario(
    dados: UsuarioCriar,
    is_admin: bool = False,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).cadastro(dados, is_admin=is_admin)


# ------------------------------------------------------------------
# EdicaoUsuario()
# ------------------------------------------------------------------
@router.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResposta,
    summary="Editar dados de um usuário (admin)",
)
def edicao_usuario(
    usuario_id: int,
    dados: UsuarioAtualizar,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).edicao(usuario_id, dados)


# ------------------------------------------------------------------
# alterarPermissoes()
# ------------------------------------------------------------------
@router.patch(
    "/usuarios/{usuario_id}/permissoes",
    response_model=UsuarioResposta,
    summary="Alterar permissões de admin de um usuário",
)
def alterar_permissoes(
    usuario_id: int,
    payload: AlterarPermissaoSchema,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).alterar_permissoes(usuario_id, payload)


# ------------------------------------------------------------------
# Desativar usuário (soft delete)
# ------------------------------------------------------------------
@router.patch(
    "/usuarios/{usuario_id}/desativar",
    response_model=UsuarioResposta,
    summary="Desativar conta de um usuário",
)
def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).desativar(usuario_id)


# ------------------------------------------------------------------
# Deletar permanentemente
# ------------------------------------------------------------------
@router.delete(
    "/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário permanentemente (admin)",
)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    FacadeService.get_instance(db).deletar(usuario_id)

# ------------------------------------------------------------------
# contar_entidades()  –  totais por tipo
# ------------------------------------------------------------------
@router.get(
    "/entidades/contagem",
    summary="Quantidade de entidades cadastradas no sistema",
)
def contar_entidades(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    return FacadeService.get_instance(db).contar_entidades()


# ------------------------------------------------------------------
# estatisticas_cache()  –  demonstração do cache RAM
# ------------------------------------------------------------------
@router.get(
    "/cache/estatisticas",
    summary="Estatísticas do cache RAM (demonstração armazenamento em memória)",
)
def estatisticas_cache(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_atual),
):
    """
    Demonstra que o sistema utiliza armazenamento em RAM (cache) 
    além da persistência em SQLite.
    """
    return FacadeService.get_instance(db).obter_estatisticas_cache()
