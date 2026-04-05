"""Testes do Template Method de exportação (NoteExporter)."""

from __future__ import annotations

import pytest

from app.models.note import Note
from app.patterns.export import PdfNoteExporter, PlainTextNoteExporter


def make_note(
    title: str = "Minha Nota",
    content: str = "Conteudo da nota.",
    attachments: list[str] | None = None,
) -> Note:
    return Note(
        note_id="abc123",
        owner="joao",
        title=title,
        content=content,
        attachments=attachments or [],
    )


# ---------------------------------------------------------------------------
# PlainTextNoteExporter
# ---------------------------------------------------------------------------

class TestPlainTextNoteExporter:
    def test_retorna_bytes(self):
        result = PlainTextNoteExporter().export(make_note())
        assert isinstance(result, bytes)

    def test_contem_titulo(self):
        result = PlainTextNoteExporter().export(make_note(title="Titulo Especial"))
        assert b"Titulo Especial" in result

    def test_contem_owner(self):
        result = PlainTextNoteExporter().export(make_note())
        assert b"joao" in result

    def test_contem_conteudo(self):
        result = PlainTextNoteExporter().export(make_note(content="Texto importante"))
        assert b"Texto importante" in result

    def test_sem_anexos_nao_inclui_secao_anexos(self):
        result = PlainTextNoteExporter().export(make_note(attachments=[]))
        assert b"Anexos" not in result

    def test_com_anexos_lista_nomes(self):
        result = PlainTextNoteExporter().export(make_note(attachments=["foto.png", "doc.pdf"]))
        assert b"foto.png" in result
        assert b"doc.pdf" in result

    def test_contem_rodape_gerado_em(self):
        result = PlainTextNoteExporter().export(make_note())
        assert b"Gerado em" in result

    def test_exportacoes_independentes_nao_acumulam_estado(self):
        exporter = PlainTextNoteExporter()
        r1 = exporter.export(make_note(title="Nota A"))
        r2 = exporter.export(make_note(title="Nota B"))
        assert b"Nota A" not in r2
        assert b"Nota B" not in r1

    def test_caracteres_especiais_nao_causam_erro(self):
        note = make_note(title="Título com açúcar", content="Ênfase em ação")
        result = PlainTextNoteExporter().export(note)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# PdfNoteExporter
# ---------------------------------------------------------------------------

class TestPdfNoteExporter:
    def test_retorna_bytes(self):
        result = PdfNoteExporter().export(make_note())
        assert isinstance(result, bytes)

    def test_assinatura_pdf_valida(self):
        result = PdfNoteExporter().export(make_note())
        assert result[:4] == b"%PDF"

    def test_nota_sem_anexos_nao_lanca_erro(self):
        PdfNoteExporter().export(make_note(attachments=[]))  # sem erro

    def test_nota_com_multiplos_anexos_nao_lanca_erro(self):
        anexos = ["foto.png", "relatorio.pdf", "mapa.shp"]
        PdfNoteExporter().export(make_note(attachments=anexos))  # sem erro

    def test_exportacoes_independentes_produzem_bytes_distintos(self):
        r1 = PdfNoteExporter().export(make_note(title="Nota A"))
        r2 = PdfNoteExporter().export(make_note(title="Nota B"))
        assert r1 != r2

    def test_conteudo_longo_nao_lanca_erro(self):
        conteudo_longo = "Linha de texto. " * 300
        PdfNoteExporter().export(make_note(content=conteudo_longo))  # sem erro


# ---------------------------------------------------------------------------
# Contrato do Template Method
# ---------------------------------------------------------------------------

class TestNoteExporterContrato:
    """Garante que ambas as implementações honram o contrato da classe base."""

    @pytest.mark.parametrize("exporter_cls", [PlainTextNoteExporter, PdfNoteExporter])
    def test_export_retorna_bytes_nao_vazios(self, exporter_cls):
        result = exporter_cls().export(make_note())
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.parametrize("exporter_cls", [PlainTextNoteExporter, PdfNoteExporter])
    def test_export_nota_sem_conteudo_nao_lanca_erro(self, exporter_cls):
        note = make_note(title="Vazia", content="")
        exporter_cls().export(note)  # sem erro
