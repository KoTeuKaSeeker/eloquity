from abc import ABC, abstractmethod
from typing import List
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext._handlers.basehandler import BaseHandler

class CommandInterface(ABC):

    @abstractmethod
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    @abstractmethod
    def get_telegram_handlers(self) -> List[BaseHandler]:
        pass