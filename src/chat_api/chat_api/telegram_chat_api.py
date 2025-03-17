from telegram import Update, Message
from typing import Dict, List
from src.chat_api.chat_api.chat_api_interface import ChatApiInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from telegram.ext import Application, filters, CallbackContext, ConversationHandler, MessageHandler
from src.format_handlers_manager import FormatHandlersManager
from src.chat_api.chat.telegram_chat import TelegramChat
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class UniversalFilter(filters.MessageFilter):
    message_filter: MessageFilterInterface
    telegram_chat_api: "TelegramChatApi"

    def __init__(self, message_filter: MessageFilterInterface, telegram_chat_api: "TelegramChatApi"):
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
        if telegram_message.entities[0].type == "audio": message["audio_path"] = telegram_message["text"]
        elif telegram_message.text: message["text"] = telegram_message.text
        else: message["audio_path"] = self.format_handler.load_audio(telegram_message)
        return message

    def _get_telegram_handler_function(self, message_handler: MessageHandlerInterface):
        def telegram_handler_function(update: Update, context: CallbackContext) -> str:
            message = self.get_message_dict(update.message)

            context = {}
            context["user_id"] = update.effective_user.id

            chat = TelegramChat(update, context)

            state = message_handler.get_message_handler(message, context, chat)
            return state
        
        return telegram_handler_function
    
    def _get_telegram_filter(self, message_hander: MessageHandlerInterface) -> filters.MessageFilter:
        message_filter = message_hander.get_message_filter()
        telegam_filter = UniversalFilter(message_filter, self)
        return telegam_filter


    def set_handler_states(self, handler_states: Dict[str, List[MessageHandlerInterface]]):
        clear_handler_states = handler_states.copy()
        entry_points = []
        if "entry_point"in clear_handler_states:
            entry_points = clear_handler_states["entry_point"]    
            del clear_handler_states["entry_point"]
        
        entry_point_telegram_handlers = [MessageHandler(self._get_telegram_filter(message_handler), self._get_telegram_handler_function(message_handler)) for message_handler in entry_points]
        
        clear_telegram_handler_states = {}
        for state, message_handlers in clear_handler_states:
            clear_telegram_handler_states[state] = [MessageHandler(self._get_telegram_filter(message_handler), self._get_telegram_handler_function(message_handler)) for message_handler in message_handlers]

        conversation_handler = ConversationHandler(
            entry_points=entry_point_telegram_handlers,
            states=clear_telegram_handler_states,
            fallbacks=[]
        )

        self.app.add_handler(conversation_handler)

    def start(self, poll_interval: int = 3):
        self.app.run_polling(poll_interval)