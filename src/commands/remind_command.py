from typing import List
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.ext._handlers.basehandler import BaseHandler
from src.commands.command_interface import CommandInterface
from src.conversation.conversation_states_manager import ConversationState

class RemindCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏮️ Для начала работы с ботом выполните команду /start")

    def get_entry_points(self) -> List[BaseHandler]:
        return [MessageHandler(filters.ALL, self.handle_command)]