"""Template Method para exportação de notas.

A classe abstrata NoteExporter define o esqueleto do algoritmo de exportação
em três passos fixos (cabeçalho → corpo → rodapé), deixando cada etapa para
as subclasses especializarem.

Implementações concretas:
- PdfNoteExporter  : gera um arquivo PDF usando fpdf2
- PlainTextNoteExporter: gera texto simples (útil para testes e debug)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.note import Note


class NoteExporter(ABC):
    """Classe base com o Template Method de exportação."""

    # ------------------------------------------------------------------ #
    # Template Method — não deve ser sobrescrito                          #
    # ------------------------------------------------------------------ #

    def export(self, note: Note) -> bytes:
        """Esqueleto do algoritmo: setup → cabeçalho → corpo → rodapé → build."""
        self._setup(note)
        self._write_header(note)
        self._write_body(note)
        self._write_footer(note)
        return self._build()

    # ------------------------------------------------------------------ #
    # Hooks e passos abstratos                                            #
    # ------------------------------------------------------------------ #

    def _setup(self, note: Note) -> None:
        """Hook opcional: inicializa recursos antes de escrever (ex: objeto PDF)."""

    @abstractmethod
    def _write_header(self, note: Note) -> None:
        """Escreve título, autor e data de atualização."""

    @abstractmethod
    def _write_body(self, note: Note) -> None:
        """Escreve o conteúdo principal e lista de anexos."""

    @abstractmethod
    def _write_footer(self, note: Note) -> None:
        """Escreve rodapé com data de geração do documento."""

    @abstractmethod
    def _build(self) -> bytes:
        """Serializa o documento acumulado e retorna os bytes finais."""


# ------------------------------------------------------------------ #
# Implementação PDF                                                    #
# ------------------------------------------------------------------ #

class PdfNoteExporter(NoteExporter):
    """Exporta a nota como PDF usando fpdf2."""

    def _setup(self, note: Note) -> None:
        from fpdf import FPDF  # import local — fpdf2 é opcional

        self._pdf = FPDF()
        self._pdf.set_auto_page_break(auto=True, margin=15)
        self._pdf.add_page()
        self._pdf.set_margins(left=20, top=20, right=20)

    def _write_header(self, note: Note) -> None:
        from fpdf.enums import XPos, YPos

        pdf = self._pdf

        pdf.set_font("Helvetica", style="B", size=18)
        pdf.multi_cell(0, 10, note.title, align="L")
        pdf.ln(2)

        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Autor: {note.owner}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(
            0, 6,
            f"Ultima atualizacao: {note.updated_at.strftime('%d/%m/%Y %H:%M')}",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.3)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(6)

    def _write_body(self, note: Note) -> None:
        from fpdf.enums import XPos, YPos

        pdf = self._pdf

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, note.content)
        pdf.ln(6)

        if note.attachments:
            pdf.set_font("Helvetica", style="B", size=10)
            pdf.cell(0, 6, "Anexos:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", size=10)
            for attachment in note.attachments:
                pdf.cell(0, 6, f"  - {attachment}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(4)

    def _write_footer(self, note: Note) -> None:
        from fpdf.enums import XPos, YPos

        pdf = self._pdf
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")

        pdf.set_font("Helvetica", style="I", size=8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 6, f"Documento gerado em {now}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)

    def _build(self) -> bytes:
        return bytes(self._pdf.output())


# ------------------------------------------------------------------ #
# Implementação texto simples (útil em testes e fallback)             #
# ------------------------------------------------------------------ #

class PlainTextNoteExporter(NoteExporter):
    """Exporta a nota como texto puro (.txt)."""

    def _setup(self, note: Note) -> None:
        self._lines: list[str] = []

    def _write_header(self, note: Note) -> None:
        sep = "=" * 60
        self._lines += [
            sep,
            f"TITULO : {note.title}",
            f"AUTOR  : {note.owner}",
            f"UPDATED: {note.updated_at.strftime('%d/%m/%Y %H:%M')}",
            sep,
            "",
        ]

    def _write_body(self, note: Note) -> None:
        self._lines.append(note.content)
        self._lines.append("")
        if note.attachments:
            self._lines.append("Anexos:")
            for a in note.attachments:
                self._lines.append(f"  - {a}")
            self._lines.append("")

    def _write_footer(self, note: Note) -> None:
        now = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
        self._lines += ["-" * 60, f"Gerado em {now}"]

    def _build(self) -> bytes:
        return "\n".join(self._lines).encode("utf-8")
