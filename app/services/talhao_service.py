from __future__ import annotations

import json
import uuid
from typing import List, Optional, Tuple

from app.models.talhao import Talhao
from app.repository.talhao_repository import TalhaoRepository


class TalhaoService:
    def __init__(self, repository: TalhaoRepository) -> None:
        self._repo = repository

    def criar_talhao(
        self,
        nome: str,
        variedade_cana: str,
        idade: int,
        ultima_colheita: str,
        solo: str,
        status: str,
        previsao_colheita: str,
        irrigacao: bool,
    ) -> Talhao:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome do talhao nao pode ser vazio.")
        talhao = Talhao(
            talhao_id=str(uuid.uuid4()),
            nome=nome,
            variedade_cana=variedade_cana.strip(),
            idade=int(idade),
            ultima_colheita=ultima_colheita.strip(),
            solo=solo.strip(),
            status=status,
            previsao_colheita=previsao_colheita.strip(),
            irrigacao=bool(irrigacao),
        )
        self._repo.create(talhao)
        return talhao

    def listar_talhoes(self) -> List[Talhao]:
        return sorted(self._repo.list_all(), key=lambda t: t.nome.lower())

    def get_talhao(self, talhao_id: str) -> Optional[Talhao]:
        return self._repo.get(talhao_id)

    def atualizar_talhao(
        self,
        talhao_id: str,
        nome: str | None = None,
        variedade_cana: str | None = None,
        idade: int | None = None,
        ultima_colheita: str | None = None,
        solo: str | None = None,
        status: str | None = None,
        previsao_colheita: str | None = None,
        irrigacao: bool | None = None,
    ) -> Talhao:
        talhao = self._repo.get(talhao_id)
        if not talhao:
            raise ValueError(f"Talhao {talhao_id} nao encontrado.")
        if nome is not None:
            talhao.nome = nome.strip()
        if variedade_cana is not None:
            talhao.variedade_cana = variedade_cana.strip()
        if idade is not None:
            talhao.idade = int(idade)
        if ultima_colheita is not None:
            talhao.ultima_colheita = ultima_colheita.strip()
        if solo is not None:
            talhao.solo = solo.strip()
        if status is not None:
            talhao.status = status
        if previsao_colheita is not None:
            talhao.previsao_colheita = previsao_colheita.strip()
        if irrigacao is not None:
            talhao.irrigacao = bool(irrigacao)
        self._repo.update(talhao)
        return talhao

    def remover_talhao(self, talhao_id: str) -> None:
        self._repo.remove(talhao_id)

    def importar_json(self, path: str) -> Tuple[int, List[str]]:
        """Importa lista de talhões de um arquivo JSON.

        Retorna (quantidade criada, lista de erros).
        """
        with open(path, encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, list):
            return 0, ["O arquivo JSON deve conter uma lista de talhoes."]

        criados = 0
        erros: List[str] = []
        for i, item in enumerate(dados):
            try:
                self.criar_talhao(
                    nome=item.get("nome", ""),
                    variedade_cana=item.get("variedade_cana", ""),
                    idade=item.get("idade", 0),
                    ultima_colheita=item.get("ultima_colheita", ""),
                    solo=item.get("solo", ""),
                    status=item.get("status", "Ativo"),
                    previsao_colheita=item.get("previsao_colheita", ""),
                    irrigacao=item.get("irrigacao", False),
                )
                criados += 1
            except (ValueError, KeyError, TypeError) as exc:
                erros.append(f"Item {i + 1}: {exc}")

        return criados, erros
