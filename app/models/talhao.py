from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Talhao:
    talhao_id: str
    nome: str
    variedade_cana: str
    idade: int
    ultima_colheita: str        # "YYYY-MM-DD"
    solo: str
    status: str                 # "Ativo" | "Em colheita" | "Pousio" | "Replantio"
    previsao_colheita: str      # "YYYY-MM-DD"
    irrigacao: bool
    criado_em: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "talhao_id": self.talhao_id,
            "nome": self.nome,
            "variedade_cana": self.variedade_cana,
            "idade": self.idade,
            "ultima_colheita": self.ultima_colheita,
            "solo": self.solo,
            "status": self.status,
            "previsao_colheita": self.previsao_colheita,
            "irrigacao": self.irrigacao,
            "criado_em": self.criado_em.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Talhao:
        criado_em = data.get("criado_em")
        return cls(
            talhao_id=data["talhao_id"],
            nome=data["nome"],
            variedade_cana=data["variedade_cana"],
            idade=int(data["idade"]),
            ultima_colheita=data["ultima_colheita"],
            solo=data["solo"],
            status=data["status"],
            previsao_colheita=data["previsao_colheita"],
            irrigacao=bool(data["irrigacao"]),
            criado_em=datetime.fromisoformat(criado_em) if criado_em else datetime.utcnow(),
        )
