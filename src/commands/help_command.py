from typing import List
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.ext._handlers.basehandler import BaseHandler
from src.commands.command_interface import CommandInterface

class HelpCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("This is a help command!")

    def get_telegram_handler(self) -> BaseHandler:
        return CommandHandler('help', self.handle_command)