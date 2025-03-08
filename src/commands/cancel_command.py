from typing import List, Dict
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.ext._handlers.basehandler import BaseHandler
from src.commands.command_interface import CommandInterface
from src.conversation.conversation_states_manager import ConversationState

class CancelCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Нечего отменять 😁")
    
    def get_conversation_states(self) -> Dict[str, BaseHandler]:
        return {
            ConversationState.waiting: [CommandHandler('cancel', self.handle_command)]
        }