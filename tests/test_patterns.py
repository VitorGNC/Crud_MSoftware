"""Testes dos design patterns: Command, Memento, Observer, Factory e Sender."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.models.note import Note
from app.patterns.command import (
    CommandInvoker,
    CreateNoteCommand,
    DeleteNoteCommand,
    UpdateNoteCommand,
)
from app.patterns.factory import CommandFactory
from app.patterns.memento import NoteCaretaker, NoteMemento
from app.patterns.observer import (
    EventoNota,
    LogNoteObserver,
    NoteEventBus,
    StatisticsObserver,
)
from app.patterns.receiver import NoteReceiver
from app.patterns.sender import CommandSender
from app.repository.note_repository import NoteRepository
from app.repository.strategies import InMemoryStorageStrategy
from app.services.note_service import NoteService
from app.utils.logger_adapter import ConsoleLogTarget, LoggerAdapter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_logger() -> LoggerAdapter:
    return LoggerAdapter(ConsoleLogTarget())


def make_receiver() -> NoteReceiver:
    repo = NoteRepository(InMemoryStorageStrategy())
    service = NoteService(repo, make_logger())
    return NoteReceiver(service)


def make_note(note_id: str = "n1") -> Note:
    return Note(note_id=note_id, owner="joao", title="Titulo", content="Conteudo")


@pytest.fixture(autouse=True)
def limpar_observers():
    NoteEventBus._observadores.clear()
    yield
    NoteEventBus._observadores.clear()


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class TestCreateNoteCommand:
    def test_execute_cria_nota(self):
        receiver = make_receiver()
        cmd = CreateNoteCommand(receiver, "joao", "Titulo", "Conteudo")
        note = cmd.execute()
        assert note.owner == "joao"
        assert note.title == "Titulo"

    def test_undo_remove_nota_criada(self):
        receiver = make_receiver()
        cmd = CreateNoteCommand(receiver, "joao", "Titulo", "Conteudo")
        note = cmd.execute()
        cmd.undo(None)
        assert receiver._service.get_note(note.note_id) is None

    def test_snapshot_retorna_none(self):
        receiver = make_receiver()
        cmd = CreateNoteCommand(receiver, "joao", "Titulo", "Conteudo")
        assert cmd.snapshot() is None


class TestUpdateNoteCommand:
    def test_execute_atualiza_nota(self):
        receiver = make_receiver()
        note = receiver.create("joao", "Original", "Conteudo")
        cmd = UpdateNoteCommand(receiver, note.note_id, "Novo titulo", "Novo conteudo")
        atualizada = cmd.execute()
        assert atualizada.title == "Novo titulo"

    def test_snapshot_captura_estado_antes_da_atualizacao(self):
        receiver = make_receiver()
        note = receiver.create("joao", "Original", "Conteudo")
        cmd = UpdateNoteCommand(receiver, note.note_id, "Novo titulo", "Novo conteudo")
        memento = cmd.snapshot()
        assert memento is not None
        assert memento.state["title"] == "Original"

    def test_undo_restaura_estado_anterior(self):
        receiver = make_receiver()
        note = receiver.create("joao", "Original", "Conteudo")
        cmd = UpdateNoteCommand(receiver, note.note_id, "Novo titulo", "Novo conteudo")
        memento = cmd.snapshot()
        cmd.execute()
        cmd.undo(memento)
        restaurada = receiver._service.get_note(note.note_id)
        assert restaurada.title == "Original"


class TestDeleteNoteCommand:
    def test_execute_remove_nota(self):
        receiver = make_receiver()
        note = receiver.create("joao", "Titulo", "Conteudo")
        cmd = DeleteNoteCommand(receiver, note.note_id)
        cmd.execute()
        assert receiver._service.get_note(note.note_id) is None

    def test_undo_restaura_nota_removida(self):
        receiver = make_receiver()
        note = receiver.create("joao", "Titulo", "Conteudo")
        cmd = DeleteNoteCommand(receiver, note.note_id)
        memento = cmd.snapshot()
        cmd.execute()
        cmd.undo(memento)
        restaurada = receiver._service.get_note(note.note_id)
        assert restaurada is not None
        assert restaurada.title == "Titulo"


# ---------------------------------------------------------------------------
# Memento
# ---------------------------------------------------------------------------

class TestNoteMemento:
    def test_from_note_captura_estado(self):
        note = make_note()
        memento = NoteMemento.from_note(note)
        assert memento.note_id == "n1"
        assert memento.state["title"] == "Titulo"

    def test_to_note_restaura_nota(self):
        note = make_note()
        memento = NoteMemento.from_note(note)
        restaurada = memento.to_note()
        assert restaurada.note_id == note.note_id
        assert restaurada.title == note.title

    def test_memento_isola_estado(self):
        note = make_note()
        memento = NoteMemento.from_note(note)
        note.title = "Alterado"
        assert memento.state["title"] == "Titulo"


class TestNoteCaretaker:
    def test_push_e_pop(self):
        caretaker = NoteCaretaker()
        note = make_note()
        memento = NoteMemento.from_note(note)
        caretaker.push(memento)
        result = caretaker.pop()
        assert result is not None
        _, recovered = result
        assert recovered.note_id == "n1"

    def test_pop_em_caretaker_vazio_retorna_none(self):
        caretaker = NoteCaretaker()
        assert caretaker.pop() is None

    def test_history_for_retorna_historico_da_nota(self):
        caretaker = NoteCaretaker()
        m1 = NoteMemento.from_note(make_note("n1"))
        m2 = NoteMemento.from_note(make_note("n2"))
        caretaker.push(m1)
        caretaker.push(m2)
        history = caretaker.history_for("n1")
        assert len(history) == 1
        assert history[0].note_id == "n1"

    def test_pop_remove_do_historico_por_nota(self):
        caretaker = NoteCaretaker()
        memento = NoteMemento.from_note(make_note("n1"))
        caretaker.push(memento)
        caretaker.pop()
        assert caretaker.history_for("n1") == []


# ---------------------------------------------------------------------------
# Observer
# ---------------------------------------------------------------------------

class TestLogNoteObserver:
    def test_notificar_chama_logger_info(self):
        mock_logger = MagicMock()
        observer = LogNoteObserver(mock_logger)
        observer.notificar(EventoNota.CRIADA, {"note_id": "n1"})
        mock_logger.info.assert_called_once()
        mensagem = mock_logger.info.call_args[0][0]
        assert "CRIADA" in mensagem


class TestStatisticsObserver:
    def test_contabiliza_eventos(self):
        observer = StatisticsObserver()
        observer.notificar(EventoNota.CRIADA, {})
        observer.notificar(EventoNota.CRIADA, {})
        observer.notificar(EventoNota.ATUALIZADA, {})
        stats = observer.get_stats()
        assert stats["CRIADA"] == 2
        assert stats["ATUALIZADA"] == 1

    def test_evento_nao_emitido_nao_aparece(self):
        observer = StatisticsObserver()
        observer.notificar(EventoNota.CRIADA, {})
        stats = observer.get_stats()
        assert "REMOVIDA" not in stats


class TestNoteEventBus:
    def test_emitir_notifica_todos_observers(self):
        obs1 = MagicMock()
        obs2 = MagicMock()
        NoteEventBus.registrar(obs1)
        NoteEventBus.registrar(obs2)
        NoteEventBus.emitir(EventoNota.CRIADA, {"note_id": "n1"})
        obs1.notificar.assert_called_once_with(EventoNota.CRIADA, {"note_id": "n1"})
        obs2.notificar.assert_called_once_with(EventoNota.CRIADA, {"note_id": "n1"})

    def test_desregistrar_remove_observer(self):
        obs = MagicMock()
        NoteEventBus.registrar(obs)
        NoteEventBus.desregistrar(obs)
        NoteEventBus.emitir(EventoNota.CRIADA, {})
        obs.notificar.assert_not_called()

    def test_get_stats_retorna_contadores(self):
        stats_obs = StatisticsObserver()
        NoteEventBus.registrar(stats_obs)
        NoteEventBus.emitir(EventoNota.CRIADA, {})
        NoteEventBus.emitir(EventoNota.REMOVIDA, {})
        stats = NoteEventBus.get_stats()
        assert stats["CRIADA"] == 1
        assert stats["REMOVIDA"] == 1

    def test_get_stats_sem_observer_retorna_vazio(self):
        assert NoteEventBus.get_stats() == {}


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestCommandFactory:
    def setup_method(self):
        self.factory = CommandFactory(make_receiver())

    def test_create_note_retorna_tipo_correto(self):
        cmd = self.factory.create_note("joao", "T", "C")
        assert isinstance(cmd, CreateNoteCommand)

    def test_update_note_retorna_tipo_correto(self):
        cmd = self.factory.update_note("n1", "T", "C")
        assert isinstance(cmd, UpdateNoteCommand)

    def test_delete_note_retorna_tipo_correto(self):
        cmd = self.factory.delete_note("n1")
        assert isinstance(cmd, DeleteNoteCommand)

    def test_factory_propaga_receiver(self):
        receiver = make_receiver()
        factory = CommandFactory(receiver)
        cmd = factory.create_note("joao", "T", "C")
        assert cmd.receiver is receiver


# ---------------------------------------------------------------------------
# Sender + CommandInvoker (integração)
# ---------------------------------------------------------------------------

class TestCommandSender:
    def test_dispatch_executa_comando(self):
        receiver = make_receiver()
        sender = CommandSender(CommandInvoker(NoteCaretaker()))
        factory = CommandFactory(receiver)
        note = sender.dispatch(factory.create_note("joao", "Titulo", "Conteudo"))
        assert note.title == "Titulo"

    def test_undo_last_desfaz_criacao(self):
        receiver = make_receiver()
        sender = CommandSender(CommandInvoker(NoteCaretaker()))
        factory = CommandFactory(receiver)
        note = sender.dispatch(factory.create_note("joao", "Titulo", "Conteudo"))
        sender.undo_last()
        assert receiver._service.get_note(note.note_id) is None

    def test_undo_last_sem_historico_retorna_false(self):
        sender = CommandSender(CommandInvoker(NoteCaretaker()))
        assert sender.undo_last() is False

    def test_history_for_retorna_mementos_apos_update(self):
        receiver = make_receiver()
        sender = CommandSender(CommandInvoker(NoteCaretaker()))
        factory = CommandFactory(receiver)
        note = sender.dispatch(factory.create_note("joao", "Titulo", "Conteudo"))
        sender.dispatch(factory.update_note(note.note_id, "Novo", "Conteudo"))
        history = sender.history_for(note.note_id)
        assert len(history) >= 1
