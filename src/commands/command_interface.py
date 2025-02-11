from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

class CommandInterface(ABC):

    @abstractmethod
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass