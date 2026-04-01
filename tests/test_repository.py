"""Testes dos repositorios usando armazenamento em RAM."""

import pytest

from app.models.note import Note
from app.models.usuario import Usuario
from app.repository.note_repository import NoteRepository
from app.repository.strategies import InMemoryStorageStrategy
from app.repository.user_repository import UserRepository


def make_note_repo() -> NoteRepository:
    return NoteRepository(InMemoryStorageStrategy())


def make_user_repo() -> UserRepository:
    return UserRepository(InMemoryStorageStrategy())


def make_note(note_id: str = "n1", owner: str = "joao") -> Note:
    return Note(note_id=note_id, owner=owner, title="Titulo", content="Conteudo")


def make_usuario(login: str = "joao") -> Usuario:
    return Usuario(login=login, nome="Joao", email="joao@email.com", senha_hash="x", idade=20)


class TestNoteRepository:
    def test_criar_e_buscar(self):
        repo = make_note_repo()
        repo.create(make_note())
        assert repo.get("n1") is not None

    def test_listar_por_owner(self):
        repo = make_note_repo()
        repo.create(make_note("n1", "joao"))
        repo.create(make_note("n2", "joao"))
        repo.create(make_note("n3", "maria"))
        assert len(repo.list_by_owner("joao")) == 2

    def test_atualizar_nota(self):
        repo = make_note_repo()
        note = make_note()
        repo.create(note)
        note.title = "Novo titulo"
        repo.update(note)
        assert repo.get("n1").title == "Novo titulo"

    def test_remover_nota(self):
        repo = make_note_repo()
        repo.create(make_note())
        repo.remove("n1")
        assert repo.get("n1") is None

    def test_remover_nota_inexistente_lanca_erro(self):
        repo = make_note_repo()
        with pytest.raises(KeyError):
            repo.remove("inexistente")

    def test_all_notes(self):
        repo = make_note_repo()
        repo.create(make_note("n1"))
        repo.create(make_note("n2"))
        assert len(repo.all_notes()) == 2


class TestUserRepository:
    def test_adicionar_e_buscar(self):
        repo = make_user_repo()
        repo.add(make_usuario())
        assert repo.get("joao") is not None

    def test_exists(self):
        repo = make_user_repo()
        repo.add(make_usuario())
        assert repo.exists("joao") is True
        assert repo.exists("maria") is False

    def test_all_retorna_todos(self):
        repo = make_user_repo()
        repo.add(make_usuario("joao"))
        repo.add(make_usuario("maria"))
        assert len(repo.all()) == 2

    def test_remover_usuario(self):
        repo = make_user_repo()
        repo.add(make_usuario())
        repo.remove("joao")
        assert repo.exists("joao") is False
