from __future__ import annotations

from abc import ABC, abstractmethod

import uvicorn

from app.interface.api import create_api_app
from app.interface.gui import NotesAppGUI


class InterfaceStrategy(ABC):
    @abstractmethod
    def run(self, sender, receiver, note_service, user_service) -> None:
        ...


class GuiInterfaceStrategy(InterfaceStrategy):
    def run(self, sender, receiver, note_service, user_service) -> None:
        app = NotesAppGUI(sender, receiver, note_service, user_service)
        app.run()


class RestApiInterfaceStrategy(InterfaceStrategy):
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
        self.host = host
        self.port = port
        self.reload = reload

    def run(self, sender, receiver, note_service, user_service) -> None:
        api_app = create_api_app(sender, receiver, note_service, user_service)
        uvicorn.run(api_app, host=self.host, port=self.port, reload=self.reload)
