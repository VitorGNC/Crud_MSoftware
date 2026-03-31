"""Testes das entidades Usuario e Note."""

import pytest

from app.models.note import Note
from app.models.usuario import Usuario, UsuarioErro


class TestUsuarioValidacaoLogin:
    def test_login_vazio_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="vazio"):
            Usuario(login="", nome="Joao", email="joao@email.com", senha_hash="x", idade=20)

    def test_login_com_numero_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="numeros"):
            Usuario(login="joao1", nome="Joao", email="joao@email.com", senha_hash="x", idade=20)

    def test_login_acima_de_12_chars_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="12"):
            Usuario(login="abcdefghijklm", nome="Joao", email="joao@email.com", senha_hash="x", idade=20)

    def test_login_valido_cria_usuario(self):
        u = Usuario(login="joao", nome="Joao", email="joao@email.com", senha_hash="x", idade=20)
        assert u.login == "joao"


class TestUsuarioValidacaoEmail:
    def test_email_sem_arroba_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="Email"):
            Usuario(login="joao", nome="Joao", email="emailinvalido", senha_hash="x", idade=20)

    def test_email_sem_dominio_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="Email"):
            Usuario(login="joao", nome="Joao", email="joao@", senha_hash="x", idade=20)

    def test_email_sem_ponto_no_dominio_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="Email"):
            Usuario(login="joao", nome="Joao", email="joao@dominio", senha_hash="x", idade=20)

    def test_email_valido(self):
        u = Usuario(login="joao", nome="Joao", email="joao@email.com", senha_hash="x", idade=20)
        assert u.email == "joao@email.com"


class TestUsuarioValidacaoIdade:
    def test_idade_negativa_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="Idade"):
            Usuario(login="joao", nome="Joao", email="joao@email.com", senha_hash="x", idade=-1)

    def test_idade_acima_de_150_lanca_erro(self):
        with pytest.raises(UsuarioErro, match="Idade"):
            Usuario(login="joao", nome="Joao", email="joao@email.com", senha_hash="x", idade=151)

    def test_idade_limite_valida(self):
        u = Usuario(login="joao", nome="Joao", email="joao@email.com", senha_hash="x", idade=150)
        assert u.idade == 150


class TestNote:
    def test_criacao_basica(self):
        note = Note(note_id="abc", owner="joao", title="Titulo", content="Conteudo")
        assert note.note_id == "abc"
        assert note.owner == "joao"
        assert note.attachments == []

    def test_to_dict_e_from_dict(self):
        note = Note(note_id="abc", owner="joao", title="Titulo", content="Conteudo")
        restaurada = Note.from_dict(note.to_dict())
        assert restaurada.note_id == note.note_id
        assert restaurada.title == note.title
        assert restaurada.content == note.content

    def test_clone_e_independente(self):
        note = Note(note_id="abc", owner="joao", title="Titulo", content="Original")
        clone = note.clone()
        clone.content = "Modificado"
        assert note.content == "Original"
