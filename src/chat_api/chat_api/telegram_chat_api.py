from telegram import Update, Message
from typing import Dict, List
from src.chat_api.chat_api.chat_api_interface import ChatApiInterface
from telegram.ext import Application, filters, CallbackContext, ConversationHandler
import telegram.ext
from src.chat_api.chat.telegram_chat import TelegramChat
from src.format_handlers_manager import FormatHandlersManager
from src.chat_api.message_handler import MessageHandler
from src.chat_api.file_containers.telegram.telegram_file_container import TelegramFileContainer
from src.chat_api.file_containers.path_file_container import PathFileContainer
import asyncio

class UniversalFilter(filters.MessageFilter):
    message_filter: MessageHandler
    telegram_chat_api: "TelegramChatApi"

    def __init__(self, message_filter: MessageHandler, telegram_chat_api: "TelegramChatApi"):
        self.message_filter = message_filter
        self.telegram_chat_api = telegram_chat_api

    def filter(self, message: Message):
        message_dict = self.telegram_chat_api.get_message_dict(message)
        result = self.message_filter.filter(message_dict)

        return result

class TelegramChatApi(ChatApiInterface):
    app: Application
    format_handler: FormatHandlersManager

    def __init__(self, token: str, audio_dir: str, video_dir: str, audio_extenstion: str):
        self.app = Application.builder().token(token).build()
        self.format_handler = FormatHandlersManager(audio_dir, video_dir, audio_extenstion)

    def get_message_dict(self, telegram_message: Message):
        message = {}
        if len(telegram_message.entities) > 0 and telegram_message.entities[0].type == "audio": message["audio_container"] = PathFileContainer(telegram_message["text"])
        elif telegram_message.text: message["text"] = telegram_message.text
        else: message["audio_container"] = TelegramFileContainer(telegram_message, self.format_handler)

        if telegram_message.forward_origin: message["forward_origin_date"] = telegram_message.forward_origin.date
        message["date"] = telegram_message.date
        return message

    def _get_telegram_handler_function(self, message_handler: MessageHandler):
        async def telegram_handler_function(update: Update, t_context: CallbackContext) -> str:
            message = self.get_message_dict(update.message)

            context = {}
            context["user_id"] = update.effective_user.id
            context["user_data"] = t_context.user_data

            chat = TelegramChat(update, t_context)

            state = await message_handler.get_message_handler()(message, context, chat)
            return state
        
        return telegram_handler_function
    
    def _get_telegram_filter(self, message_hander: MessageHandler) -> filters.MessageFilter:
        message_filter = message_hander.get_message_filter()
        telegam_filter = UniversalFilter(message_filter, self)
        return telegam_filter


    def set_handler_states(self, handler_states: Dict[str, List[MessageHandler]]):
        clear_handler_states = handler_states.copy()
        entry_points = []
        if "entry_point"in clear_handler_states:
            entry_points = clear_handler_states["entry_point"]    
            del clear_handler_states["entry_point"]
        
        entry_point_telegram_handlers = [telegram.ext.MessageHandler(self._get_telegram_filter(message_handler), self._get_telegram_handler_function(message_handler)) for message_handler in entry_points]
        
        clear_telegram_handler_states = {}
        for state, message_handlers in clear_handler_states.items():
            clear_telegram_handler_states[state] = [telegram.ext.MessageHandler(self._get_telegram_filter(message_handler), self._get_telegram_handler_function(message_handler)) for message_handler in message_handlers]

        conversation_handler = ConversationHandler(
            entry_points=entry_point_telegram_handlers,
            states=clear_telegram_handler_states,
            fallbacks=[],
        )

        self.app.add_handler(conversation_handler)

    def start(self, poll_interval: int = 3):
        self.app.run_polling(poll_interval)