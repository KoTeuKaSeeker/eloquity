from typing import Any
from src.chat_api.chat.chat_interface import ChatInterface
from telegram import Update, Message, Chat, MessageEntity, Audio, Voice, Video, Document
from telegram.ext import CallbackContext, ConversationHandler
import datetime

class TelegramChat(ChatInterface):
    update: Update
    context: CallbackContext

    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context

    async def send_message_to_query(self, message: str):
        await self.update.message.reply_text(message)

    async def send_file_to_query(self, file_path: str, file_name: str = "some_file"):
        with open(file_path, "rb") as file:
            await self.update.message.reply_document(document=file, read_timeout=10)

    async def send_message_to_event_loop(self, message: dict, context: dict, chat: ChatInterface):
        """
            Отправляет новое сообщение, которое должен увидеть сам же бот, но не пользователь (сам себе отправляет сообщение, которое поймают хендлеры).
            С помощью этой функции можно произвольно отправлять сообщеине другим хэндлерам, и, в дальнейшем, переходить на них.
        """

        text = ""
        message_entity = None
        if "command" in message:
            text = message["command"]
            message_entity = MessageEntity(type="bot_command", offset=0, length=len(text))
        if "audio_container" in message:
            text = message["audio_container"].get_file_path()
            message_entity = MessageEntity(type="audio", offset=0, length=len(text))
        if "text" in message:
            text = message["text"]

        update = Update(
            update_id=123456789,
            message=Message(
                message_id=1,
                date=datetime.datetime.now(),
                chat=Chat(id=context["user_id"], type="private"),
                from_user=context["user_id"],
                entities=[message_entity],
                text=text
            )
        )
        
        update.message._bot = self.context.bot
        await self.context.application.update_queue.put(update)

    def get_entry_point_state(self) -> Any:
        """
            Возвращает значение, которое изменяет стейт машину в состояние entry_point. Эта функция сделана специальна, так как в случа telegram это 
            не просто строка, а переменная определённого типа (которая здесь в этом случае и должна вернуться). Если же такого особого функционала нет
            (как вероятнее всего и будет в OpenWebUI), то можно просто также и вернуть строку 'entry_point'.

        """
        return ConversationHandler.END