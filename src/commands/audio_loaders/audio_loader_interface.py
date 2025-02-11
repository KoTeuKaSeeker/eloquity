from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

class AudioLoaderInterface(ABC):

    @abstractmethod
    async def load_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str | None:
        pass