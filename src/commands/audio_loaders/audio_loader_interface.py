from abc import ABC, abstractmethod
from typing import List
from src.chat_api.chat.chat_interface import ChatInterface

class AudioLoaderInterface(ABC):
    @abstractmethod
    async def load_audio(self, message: dict, context: dict, chat: ChatInterface, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str | None:
        pass