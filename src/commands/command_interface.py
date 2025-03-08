from abc import ABC, abstractmethod
from typing import List, Dict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext._handlers.basehandler import BaseHandler

class CommandInterface(ABC):
    def get_entry_points(self) -> List[BaseHandler]:
        return []

    def get_conversation_states(self) -> Dict[str, BaseHandler]:
        return {}