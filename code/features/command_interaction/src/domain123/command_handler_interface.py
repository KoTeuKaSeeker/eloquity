from abc import ABC, abstractmethod
from src.domain.handler_data_interface import HandlerDataInterface
from src.domain.navigation_data_interface import NavigationDataInterface

class CommandHandlerInterface(ABC):
    @abstractmethod
    def handle(self, handler_data: HandlerDataInterface) -> NavigationDataInterface:
        pass