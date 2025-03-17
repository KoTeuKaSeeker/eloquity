from abc import ABC, abstractmethod
from telegram import Message

class FormatHandlerInterface(ABC):
    @abstractmethod
    async def load_audio(self, message: Message) -> str:
        pass