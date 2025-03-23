from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any
from src.domain.conversation_state_interface import ConversationStateInterface
from src.outer_domain.command_handler_interface import CommandHandlerInterface

class ConversationManagerInterface(ABC):
    @abstractmethod
    def get_conversation_states(self) -> Dict[ConversationStateInterface, CommandHandlerInterface]:
        pass

    @abstractmethod
    def add_states(self, states: Dict[ConversationStateInterface, CommandHandlerInterface]):
        pass

    @abstractmethod
    def get_state(self, state: ConversationStateInterface) -> List[CommandHandlerInterface]:
        pass

    @abstractmethod
    def get_handler_functions(self) -> Dict[str, Callable[..., Any]]:
        pass