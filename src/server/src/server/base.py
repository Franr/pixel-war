from abc import ABC, abstractmethod

from shared.commands import Command

from ..game import GameHandler
from ..logger import logger


class BaseServerHandler(ABC):
    """
    Base server handler class. Should provide a way to:
    - start a server to listen connections
    - close all connections
    - broadcast messages
    """

    def __init__(self, host="127.0.0.1", port=8888) -> None:
        self.host = host
        self.port = port
        self.clients = {}
        self.gh = GameHandler(self)

    def broadcast(self, message: Command):
        logger.debug(f"[BrdCst ] M:{message}")

        for client in self.clients.values():
            client.send_message(message)

    @abstractmethod
    def close_client_connections(self):
        pass

    @abstractmethod
    async def run(self):
        pass


class BaseConnection(ABC):

    def __init__(self, clients, game_handler: GameHandler) -> None:
        super().__init__()
        self.clients = clients
        self.gh = game_handler

    @property
    @abstractmethod
    def address(self) -> tuple[str, int]:
        """
        Should return ip and port tuple.
        e.g.: ("127.0.0.1", 50023)
        """

    def register_client(self):
        self.clients[self.address] = self

    @abstractmethod
    def send_message(self, data: Command):
        """
        Send a command to the client.
        """
