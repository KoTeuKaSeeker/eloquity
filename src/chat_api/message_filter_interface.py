from abc import ABC, abstractmethod

class MessageFilterInterface(ABC):
    @abstractmethod
    def filter(self, message: dict, message_type: str, user_id: int) -> bool:
        pass