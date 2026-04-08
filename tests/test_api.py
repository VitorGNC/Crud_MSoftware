"""Testes de integração para a API REST — endpoints de Talhões e Satélite."""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.interface.api import create_api_app
from app.models.note import Note
from app.models.satellite import Anomaly, BoundingBox, NDVIResult, Severity, SatelliteImage
from app.models.talhao import Talhao
from app.models.usuario import Usuario
from app.patterns.command import CommandInvoker
from app.patterns.memento import NoteCaretaker
from app.patterns.receiver import NoteReceiver
from app.patterns.sender import CommandSender
from app.repository.note_repository import NoteRepository
from app.repository.strategies import InMemoryStorageStrategy
from app.repository.user_repository import UserRepository
from app.services.note_service import NoteService
from app.services.user_service import UserService
from app.services.talhao_service import TalhaoService
from app.repository.talhao_repository import TalhaoRepository
from app.utils.logger_adapter import ConsoleLogTarget, LoggerAdapter

import datetime
import numpy as np


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

SENHA = "Senha@123"
LOGIN = "testeapi"
EMAIL = "teste@api.com"
NOME = "Teste API"
IDADE = 25

BASIC = base64.b64encode(f"{LOGIN}:{SENHA}".encode()).decode()
AUTH_HEADERS = {"Authorization": f"Basic {BASIC}"}


@pytest.fixture()
def client():
    logger = LoggerAdapter(ConsoleLogTarget())
    note_repo = NoteRepository(InMemoryStorageStrategy())
    user_repo = UserRepository(InMemoryStorageStrategy())
    talhao_repo = TalhaoRepository(InMemoryStorageStrategy())

    note_service = NoteService(note_repo, logger)
    user_service = UserService(user_repo, logger)
    talhao_service = TalhaoService(talhao_repo)

    user_service.registrar(LOGIN, SENHA, EMAIL, NOME, IDADE)

    caretaker = NoteCaretaker()
    receiver = NoteReceiver(note_service)
    invoker = CommandInvoker(caretaker)
    sender = CommandSender(invoker)

    satellite_service = MagicMock()

    app = create_api_app(sender, receiver, note_service, user_service, talhao_service, satellite_service)
    return TestClient(app), talhao_service, satellite_service


# ─────────────────────────────────────────────────────────────
# Talhões — CRUD
# ─────────────────────────────────────────────────────────────

TALHAO_PAYLOAD = {
    "nome": "Talhao Norte",
    "variedade_cana": "RB867515",
    "idade": 3,
    "ultima_colheita": "2024-06-01",
    "solo": "Argissolo",
    "status": "Ativo",
    "previsao_colheita": "2025-06-01",
    "irrigacao": True,
}


class TestTalhaoEndpoints:

    def test_listar_talhoes_vazio(self, client):
        c, *_ = client
        resp = c.get("/talhoes", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_criar_talhao(self, client):
        c, *_ = client
        resp = c.post("/talhoes", json=TALHAO_PAYLOAD, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Talhao criado."
        assert data["talhao"]["nome"] == "Talhao Norte"
        assert "talhao_id" in data["talhao"]

    def test_listar_talhoes_apos_criacao(self, client):
        c, *_ = client
        c.post("/talhoes", json=TALHAO_PAYLOAD, headers=AUTH_HEADERS)
        resp = c.get("/talhoes", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_buscar_talhao_por_id(self, client):
        c, *_ = client
        criado = c.post("/talhoes", json=TALHAO_PAYLOAD, headers=AUTH_HEADERS).json()
        tid = criado["talhao"]["talhao_id"]
        resp = c.get(f"/talhoes/{tid}", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["talhao_id"] == tid

    def test_buscar_talhao_inexistente_retorna_404(self, client):
        c, *_ = client
        resp = c.get("/talhoes/nao-existe", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_atualizar_talhao(self, client):
        c, *_ = client
        criado = c.post("/talhoes", json=TALHAO_PAYLOAD, headers=AUTH_HEADERS).json()
        tid = criado["talhao"]["talhao_id"]
        resp = c.put(f"/talhoes/{tid}", json={"nome": "Talhao Sul", "status": "Em colheita"}, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["talhao"]["nome"] == "Talhao Sul"
        assert resp.json()["talhao"]["status"] == "Em colheita"

    def test_atualizar_talhao_inexistente_retorna_404(self, client):
        c, *_ = client
        resp = c.put("/talhoes/nao-existe", json={"nome": "X"}, headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_deletar_talhao(self, client):
        c, *_ = client
        criado = c.post("/talhoes", json=TALHAO_PAYLOAD, headers=AUTH_HEADERS).json()
        tid = criado["talhao"]["talhao_id"]
        resp = c.delete(f"/talhoes/{tid}", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Talhao removido."
        assert c.get(f"/talhoes/{tid}", headers=AUTH_HEADERS).status_code == 404

    def test_deletar_talhao_inexistente_retorna_404(self, client):
        c, *_ = client
        resp = c.delete("/talhoes/nao-existe", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_criar_talhao_nome_vazio_retorna_400(self, client):
        c, *_ = client
        payload = {**TALHAO_PAYLOAD, "nome": "   "}
        resp = c.post("/talhoes", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 400

    def test_talhoes_requer_autenticacao(self, client):
        c, *_ = client
        assert c.get("/talhoes").status_code == 401


# ─────────────────────────────────────────────────────────────
# Satélite — endpoints com mock
# ─────────────────────────────────────────────────────────────

def _fake_image():
    return SatelliteImage(
        image_id="img-001",
        product_name="S2A_MSIL2A_20240601",
        acquisition_date=datetime.datetime(2024, 6, 1),
        cloud_cover=5.0,
        bbox=BoundingBox(-7.1, -35.1, -7.0, -35.0),
        download_url="http://example.com/img",
    )


def _fake_ndvi():
    arr = np.array([[0.5, 0.1], [0.05, 0.7]])
    return NDVIResult(
        image_id="img-001",
        ndvi_array=arr,
        min_value=float(arr.min()),
        max_value=float(arr.max()),
        mean_value=float(arr.mean()),
        transform=None,
        crs="EPSG:32724",
    )


def _fake_anomaly():
    return Anomaly(
        anomaly_id="ano-001",
        image_id="img-001",
        latitude=-7.05,
        longitude=-35.05,
        ndvi_value=0.05,
        severity=Severity.HIGH,
    )


class TestSatelliteEndpoints:

    def test_listar_imagens(self, client):
        c, _, sat = client
        sat.list_images.return_value = [_fake_image()]
        resp = c.get("/satellite/images", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()[0]["image_id"] == "img-001"

    def test_listar_imagens_vazio(self, client):
        c, _, sat = client
        sat.list_images.return_value = []
        resp = c.get("/satellite/images", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_buscar_imagens(self, client):
        c, _, sat = client
        sat.configure_credentials.return_value = None
        sat.search_images.return_value = [_fake_image()]
        payload = {
            "copernicus_user": "user",
            "copernicus_password": "pass",
            "min_lat": -7.1, "min_lon": -35.1,
            "max_lat": -7.0, "max_lon": -35.0,
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
        }
        resp = c.post("/satellite/search", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()[0]["image_id"] == "img-001"

    def test_buscar_imagens_data_invalida(self, client):
        c, _, sat = client
        sat.configure_credentials.return_value = None
        payload = {
            "copernicus_user": "user",
            "copernicus_password": "pass",
            "min_lat": -7.1, "min_lon": -35.1,
            "max_lat": -7.0, "max_lon": -35.0,
            "start_date": "data-invalida",
            "end_date": "2024-06-30",
        }
        resp = c.post("/satellite/search", json=payload, headers=AUTH_HEADERS)
        assert resp.status_code == 422

    def test_configurar_credenciais(self, client):
        c, _, sat = client
        sat.configure_credentials.return_value = None
        resp = c.post(
            "/satellite/credentials",
            json={"copernicus_user": "u", "copernicus_password": "p"},
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200

    def test_configurar_credenciais_invalidas(self, client):
        c, _, sat = client
        sat.configure_credentials.side_effect = Exception("credenciais invalidas")
        resp = c.post(
            "/satellite/credentials",
            json={"copernicus_user": "u", "copernicus_password": "errada"},
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 401

    def test_processar_imagem_ndvi(self, client):
        c, _, sat = client
        sat.process_image.return_value = _fake_ndvi()
        resp = c.post("/satellite/process/img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["image_id"] == "img-001"
        assert "mean_value" in data

    def test_processar_imagem_falha_retorna_400(self, client):
        c, _, sat = client
        sat.process_image.side_effect = RuntimeError("Falha ao baixar bandas")
        resp = c.post("/satellite/process/img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 400

    def test_obter_resultado_ndvi(self, client):
        c, _, sat = client
        sat.get_result.return_value = _fake_ndvi()
        resp = c.get("/satellite/result/img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["image_id"] == "img-001"

    def test_obter_resultado_ndvi_inexistente(self, client):
        c, _, sat = client
        sat.get_result.return_value = None
        resp = c.get("/satellite/result/nao-existe", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_detectar_anomalias(self, client):
        c, _, sat = client
        sat.get_result.return_value = _fake_ndvi()
        sat.detect_anomalies.return_value = [_fake_anomaly()]
        resp = c.post("/satellite/anomalies/img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()[0]["severity"] == "high"

    def test_detectar_anomalias_sem_ndvi_retorna_404(self, client):
        c, _, sat = client
        sat.get_result.return_value = None
        resp = c.post("/satellite/anomalies/img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 404

    def test_listar_anomalias(self, client):
        c, _, sat = client
        sat.list_anomalies.return_value = [_fake_anomaly()]
        resp = c.get("/satellite/anomalies", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_listar_anomalias_filtrado_por_image_id(self, client):
        c, _, sat = client
        sat.list_anomalies.return_value = [_fake_anomaly()]
        resp = c.get("/satellite/anomalies?image_id=img-001", headers=AUTH_HEADERS)
        assert resp.status_code == 200
        sat.list_anomalies.assert_called_with("img-001")

    def test_satellite_requer_autenticacao(self, client):
        c, *_ = client
        assert c.get("/satellite/images").status_code == 401
