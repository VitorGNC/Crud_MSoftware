"""Testes da politica de senha e hashing."""

import pytest

from app.auth import hash_password, verify_password


class TestPoliticaDeSenha:
    def test_senha_curta_lanca_erro(self):
        with pytest.raises(ValueError, match="8 caracteres"):
            hash_password("Ab1!abc")

    def test_senha_sem_maiuscula_lanca_erro(self):
        with pytest.raises(ValueError, match="maiusculas"):
            hash_password("abcdefg1!")

    def test_senha_sem_minuscula_lanca_erro(self):
        with pytest.raises(ValueError, match="maiusculas"):
            hash_password("ABCDEFG1!")

    def test_senha_sem_numero_lanca_erro(self):
        with pytest.raises(ValueError, match="numeros"):
            hash_password("Abcdefg!")

    def test_senha_sem_especial_lanca_erro(self):
        with pytest.raises(ValueError, match="especial"):
            hash_password("Abcdefg1")

    def test_senha_valida_retorna_hash(self):
        resultado = hash_password("Senh@Forte1")
        assert "$" in resultado
        salt, digest = resultado.split("$", 1)
        assert len(salt) == 16
        assert len(digest) == 64


class TestVerificacaoDeSenha:
    def test_senha_correta_retorna_true(self):
        registro = hash_password("Senh@Forte1")
        assert verify_password("Senh@Forte1", registro) is True

    def test_senha_errada_retorna_false(self):
        registro = hash_password("Senh@Forte1")
        assert verify_password("SenhaErrada1!", registro) is False

    def test_registro_malformado_retorna_false(self):
        assert verify_password("Senh@Forte1", "semformatovalido") is False
