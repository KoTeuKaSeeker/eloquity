from typing import Any, List, Dict
from src.chat_api.chat.chat_interface import ChatInterface
from telegram import Update, Message, Chat, MessageEntity, Audio, Voice, Video, Document, User, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from src.chat_api.task_function import TaskFunction
import datetime
import asyncio

class TelegramChat(ChatInterface):
    update: Update
    context: CallbackContext
    max_message_length: int = 4096
    chat_functions_stack: list

    def __init__(self, update: Update, context: CallbackContext, chat_functions_stack: list):
        self.update = update
        self.context = context
        self.chat_functions_stack = chat_functions_stack

    def get_chat_functions_stack(self) -> Dict[Any, List[TaskFunction]]:
        return self.chat_functions_stack

    async def send_message_to_query(self, message: str):
        if len(message) > self.max_message_length:
            message_parts = [message[i*self.max_message_length:(i+1)*self.max_message_length] for i in range(len(message) // self.max_message_length)]
            if len(message) % self.max_message_length > 0:
                message_parts.append(message[-len(message) % self.max_message_length:])
            
            for part in message_parts:
                await self.update.message.reply_text(part, connect_timeout=60)    
        else:
            await self.update.message.reply_text(message, connect_timeout=60)

    async def send_file_to_query(self, file_path: str, file_name: str = "some_file"):
        with open(file_path, "rb") as file:
            await self.update.message.reply_document(document=file, read_timeout=60)
    
    async def send_keyboad(self, message: str, keyboard: List[List[str]]):
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await self.update.message.reply_text(message, reply_markup=reply_markup)

    async def remove_keyboad(self, message: str):
        await self.update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())

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
            text = await message["audio_container"].get_file_path()
            message_entity = MessageEntity(type="audio", offset=0, length=len(text))
        if "text" in message:
            text = message["text"]

        update = Update(
            update_id=self.update.update_id + 1,
            message=Message(
                message_id=self.update.message.message_id,
                date=datetime.datetime.now(),
                chat=self.update.effective_chat,
                message_thread_id=self.update.message.message_thread_id,
                from_user=self.update.effective_user,
                entities=[message_entity],
                text=text
            )
        )
        
        update.message._bot = self.update.message.get_bot()

        await asyncio.sleep(3)

        await self.context.application.update_queue.put(update)

    def get_entry_point_state(self) -> Any:
        """
            Возвращает значение, которое изменяет стейт машину в состояние entry_point. Эта функция сделана специальна, так как в случа telegram это 
            не просто строка, а переменная определённого типа (которая здесь в этом случае и должна вернуться). Если же такого особого функционала нет
            (как вероятнее всего и будет в OpenWebUI), то можно просто также и вернуть строку 'entry_point'.

        """
        return ConversationHandler.END