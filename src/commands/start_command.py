from typing import List
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.ext._handlers.basehandler import BaseHandler
from src.commands.command_interface import CommandInterface

class StartCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Привет. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")

    def get_telegram_handlers(self) -> List[BaseHandler]:
        return [CommandHandler('start', self.handle_command)]