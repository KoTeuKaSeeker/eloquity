from abc import ABC, abstractmethod

class ConversationStateInterface(ABC):
    @abstractmethod
    def get_state(self) -> str:
        pass
