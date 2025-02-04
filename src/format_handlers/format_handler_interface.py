from abc import ABC, abstractmethod
from telegram import Update

class FormatHandlerInterface(ABC):
    @abstractmethod
    async def load_audio(self, update: Update, context) -> str:
        pass