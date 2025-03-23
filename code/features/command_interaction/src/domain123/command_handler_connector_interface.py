from typing import Callable, Any
from abc import ABC, abstractmethod
from src.outer_domain.command_handler_interface import CommandHandlerInterface

class CommandHandlerConnectorInterface(ABC):
    @abstractmethod
    def get_handler_function(self, command_handler: CommandHandlerInterface) -> Callable[..., Any]:
        pass

