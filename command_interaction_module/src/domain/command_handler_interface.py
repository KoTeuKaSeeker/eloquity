from abc import ABC, abstractmethod
from command_interaction_module.src.outer_domain.handler_data_interface import HandlerDataInterface
from command_interaction_module.src.domain.navigation_data_interface import NavigationDataInterface

class CommandHandlerInterface(ABC):
    @abstractmethod
    def handle(self, handler_data: HandlerDataInterface) -> NavigationDataInterface:
        pass