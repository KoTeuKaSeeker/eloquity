from typing import Type
from abc import ABC, abstractmethod
from command_interaction_module.src.domain.conversation_state_interface import ConversationStateInterface
from command_interaction_module.src.domain.command_state_interface import CommandStateInterface

class NavigationDataInterface(ABC):
    @abstractmethod
    def get_next_state(self) -> ConversationStateInterface | None:
        pass

    @abstractmethod
    def get_next_command_state(self) -> CommandStateInterface | None:
        pass