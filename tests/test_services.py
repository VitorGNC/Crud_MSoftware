"""Testes das camadas de servico usando RAM."""

import pytest

from app.models.usuario import UsuarioErro
from app.patterns.observer import NoteEventBus
from app.repository.note_repository import NoteRepository
from app.repository.strategies import InMemoryStorageStrategy
from app.repository.user_repository import UserRepository
from app.services.note_service import NoteService
from app.services.user_service import UserService
from app.utils.logger_adapter import ConsoleLogTarget, LoggerAdapter


@pytest.fixture(autouse=True)
def limpar_observers():
    NoteEventBus._observadores.clear()
    yield
    NoteEventBus._observadores.clear()


def make_logger() -> LoggerAdapter:
    return LoggerAdapter(ConsoleLogTarget())


def make_user_service() -> UserService:
    return UserService(UserRepository(InMemoryStorageStrategy()), make_logger())


def make_note_service() -> NoteService:
    return NoteService(NoteRepository(InMemoryStorageStrategy()), make_logger())


class TestUserService:
    def test_registrar_usuario(self):
        svc = make_user_service()
        u = svc.registrar("joao", "Senh@Forte1", "joao@email.com", "Joao", 25)
        assert u.login == "joao"

    def test_registrar_login_duplicado_lanca_erro(self):
        svc = make_user_service()
        svc.registrar("joao", "Senh@Forte1", "joao@email.com", "Joao", 25)
        with pytest.raises(UsuarioErro, match="ja utilizado"):
            svc.registrar("joao", "Senh@Forte1", "outro@email.com", "Joao2", 30)

    def test_autenticar_com_sucesso(self):
        svc = make_user_service()
        svc.registrar("joao", "Senh@Forte1", "joao@email.com", "Joao", 25)
        u = svc.autenticar("joao", "Senh@Forte1")
        assert u.login == "joao"

    def test_autenticar_senha_errada_lanca_erro(self):
        svc = make_user_service()
        svc.registrar("joao", "Senh@Forte1", "joao@email.com", "Joao", 25)
        with pytest.raises(UsuarioErro, match="Credenciais"):
            svc.autenticar("joao", "SenhaErrada1!")

    def test_autenticar_usuario_inexistente_lanca_erro(self):
        svc = make_user_service()
        with pytest.raises(UsuarioErro, match="Credenciais"):
            svc.autenticar("naoexiste", "Senh@Forte1")

    def test_listar_retorna_todos(self):
        svc = make_user_service()
        svc.registrar("joao", "Senh@Forte1", "joao@email.com", "Joao", 25)
        svc.registrar("maria", "Senh@Forte1", "maria@email.com", "Maria", 30)
        assert len(svc.listar()) == 2


class TestNoteService:
    def test_criar_nota(self):
        svc = make_note_service()
        note = svc.create_note("joao", "Titulo", "Conteudo")
        assert note.owner == "joao"
        assert note.title == "Titulo"

    def test_criar_nota_sem_titulo_usa_padrao(self):
        svc = make_note_service()
        note = svc.create_note("joao", "", "Conteudo")
        assert note.title == "Nova nota"

    def test_listar_notas_por_owner(self):
        svc = make_note_service()
        svc.create_note("joao", "N1", "Conteudo")
        svc.create_note("joao", "N2", "Conteudo")
        svc.create_note("maria", "N3", "Conteudo")
        assert len(svc.list_notes("joao")) == 2

    def test_atualizar_nota(self):
        svc = make_note_service()
        note = svc.create_note("joao", "Original", "Conteudo")
        atualizada = svc.update_note(note.note_id, "Novo titulo", "Novo conteudo")
        assert atualizada.title == "Novo titulo"

    def test_deletar_nota(self):
        svc = make_note_service()
        note = svc.create_note("joao", "Titulo", "Conteudo")
        svc.delete_note(note.note_id)
        assert svc.get_note(note.note_id) is None

    def test_deletar_nota_inexistente_lanca_erro(self):
        svc = make_note_service()
        with pytest.raises(ValueError, match="nao encontrada"):
            svc.delete_note("id-inexistente")

    def test_attach_bytes_acima_do_limite_lanca_erro(self):
        svc = make_note_service()
        note = svc.create_note("joao", "Titulo", "Conteudo")
        payload_gigante = b"x" * (10 * 1024 * 1024 + 1)
        with pytest.raises(ValueError, match="limite"):
            svc.attach_bytes(note.note_id, "arquivo.txt", payload_gigante)

    def test_attach_bytes_vazio_lanca_erro(self):
        svc = make_note_service()
        note = svc.create_note("joao", "Titulo", "Conteudo")
        with pytest.raises(ValueError, match="vazio"):
            svc.attach_bytes(note.note_id, "arquivo.txt", b"")
