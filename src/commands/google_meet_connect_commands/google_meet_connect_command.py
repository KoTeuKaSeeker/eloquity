from typing import List, Dict, Coroutine
from src.commands.command_interface import CommandInterface
from src.google_meet.google_meet_bots_manager import GoogleMeetBotsManager
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.commands.message_transcribe_audio_with_preloaded_names_command import MessageTranscribeAudioWithPreloadedNamesCommand
from src.bitrix.bitrix_manager import BitrixManager
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.chat_api.message_handler import MessageHandler
from dataclasses import dataclass
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.chat.chat_interface import ChatInterface
import re
import datetime
import pytz
import asyncio
import time

WAITING_FOR_AUDIO, WAITING_UNTILL_HANDLING, WAITING_FOR_CONNECTION = range(3)


class GoogleMeetConnectCommand(CommandInterface):
    class UserHandleDiscription:
        bot: GoogleMeetBot
        connection_tasks: List[asyncio.Task]

        def __init__(self, bot: GoogleMeetBot, connection_tasks: List[asyncio.Task] = []):
            self.bot = bot
            self.connection_tasks = connection_tasks

    bots_manager: GoogleMeetBotsManager
    active_user_handlers: Dict[int, UserHandleDiscription]

    def __init__(self, 
                bots_manager: GoogleMeetBotsManager, 
                dropbox_manager: DropBoxManager, 
                task_extractor: TaskExtractor,
                bitrix_manager: BitrixManager, 
                transcricribe_request_log_dir: str,
                filter_factory: MessageFilterFactoryInterface,
                max_message_waiting_time: datetime.timedelta = datetime.timedelta(minutes=5),
                ):
        self.bots_manager = bots_manager
        self.max_message_waiting_time = max_message_waiting_time
        self.active_user_handlers = {}
        self.filter_factory = filter_factory

    async def connect_bot(self, update: Update, meet_link: str) -> GoogleMeetBot:
        free_bot = self.bots_manager.get_free_bot()
        
        if free_bot is None:
            await update.message.reply_text("⏮️ Не могу подключиться к конференции, так как все Google Meet боты заняты. Повторите попытку позже.")
            return None
        
        self.active_user_handlers[update.message.from_user.id] = GoogleMeetConnectCommand.UserHandleDiscription(free_bot, [asyncio.current_task()])
        await asyncio.to_thread(free_bot.connect_to_meet, meet_link)

        return free_bot
    
    async def put_update_message(self, command_text: str,  update: Update, context: ContextTypes.DEFAULT_TYPE):
        update = Update(
            update_id=123456789,
            message=Message(
                message_id=1,
                date=datetime.datetime.now(),
                chat=Chat(id=update.effective_chat.id, type="private"),
                from_user=update.effective_user,
                entities=[MessageEntity(type="bot_command", offset=0, length=len(command_text))],
                text=command_text
            )
        )

        update.message._bot = context.bot

        await context.application.update_queue.put(update)

    async def handle_meet(self, update: Update, context: ContextTypes.DEFAULT_TYPE, free_bot: GoogleMeetBot, meet_link: str):
        member_names = free_bot.get_memeber_names()[1:]
        context.user_data["preloaded_names"] = member_names

        await update.message.reply_text("✅ Обработка информации встречи завершена. Когда будете готовы, отравьте аудиозапись беседы со встречи следующим сообщением.\nЕсли же вы хотите завершить обработку встречи, выполните команду /cancel.")
        await update.message.reply_text("Для дебага: участники встречи:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(member_names)]))

        free_bot.disconnect()
        del self.active_user_handlers[update.message.from_user.id]

        await self.put_update_message("/waiting_untill_handling_continue", update, context)

    async def background_connection_to_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE, meet_link: str):
        free_bot = await self.connect_bot(update, meet_link)

        await self.print_bot_end_connection_message(update)

        meet_handling_task = asyncio.create_task(self.handle_meet(update, context, free_bot, meet_link))
        self.active_user_handlers[update.message.from_user.id].connection_tasks = [meet_handling_task]

        await self.put_update_message("/waiting_for_connection_continue", update, context)

    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        meet_link = message["text"]
        message_date = message["forward_origin_date"] if "forward_origin_date" in message else message["date"]
        message_waiting_time = datetime.datetime.now(pytz.UTC) - message_date

        if message_waiting_time > self.max_message_waiting_time:
            all_minutes, seconds = divmod(message_waiting_time.seconds, 60)
            hours, minutes = divmod(all_minutes, 60)
            days = message_waiting_time.days
            
            await chat.send_message_to_query(f"⏮️ Прошло слишком много времени с момента отправки приглашения на встречу ({days} дн. {hours} ч. {minutes} мин.), возможно встреча уже закончилась.\n❄️ Если это не так, пожалуйста, отправьте приглашение на встречу заново (не перессылкой, а новым сообщением).")
            return chat.move_back(context)

        await chat.send_message_to_query("Ссылка на Google Meet встречу была обнаружена. Подключаюсь к конференции... 🔃\nЕсли хотите отменить подключение, выполните команду /cancel.")
        
        asyncio.create_task(self.background_connection_to_bot(update, context, meet_link))

        return move_next(context, ConversationState.google_meet_waiting_for_connection, ConversationState.waiting)

    async def print_bot_end_connection_message(self, update: Update):
        await update.message.reply_text("Бот подключился к конференции 👋")

    async def waiting_for_connection_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔃 Бот ожидает подключение к встрече... Если хотите отменить обработку встречи, выполните команду /cancel.")
    
    async def waiting_for_meet_handling_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("📅 Бот находится на конференции и анализирует её. Если хотите отменить обработку встречи, выполните команду /cancel.")

    async def conversation_not_ended_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("⏮️ Пожалуйста, отправьте аудиозапись со встречи 🔖. Если хотите отменить обработку встречи, выполните команду /cancel.")

    async def connection_complete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return move_next(context, ConversationState.google_meet_waiting_untill_handling, ConversationState.waiting)
    
    async def meet_handling_complete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return move_next(context, ConversationState.message_speaker_correction_state_with_preloaded_names, ConversationState.waiting)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.from_user.id in self.active_user_handlers:
            user_handler: GoogleMeetConnectCommand.UserHandleDiscription = self.active_user_handlers[update.message.from_user.id]
            user_handler.bot.disconnect()
            for task in user_handler.connection_tasks:
                task.cancel()
            del self.active_user_handlers[update.message.from_user.id]
        await update.message.reply_text("🔖 Обработка встречи отменена.")
        return move_back(context)
    
    def get_conversation_states(self) -> Dict[str, MessageHandler]: 
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}")), self.handle_command)
            ],
            "google_meet_waiting_for_connection": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="waiting_for_connection_continue")), self.connection_complete_callback),
                MessageHandler(~self.filter_factory.create_filter("command", dict(command="cancel")), self.waiting_for_connection_message),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel)
            ],
            "google_meet_waiting_untill_handling": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="waiting_untill_handling_continue")), self.meet_handling_complete_callback),
                MessageHandler(~self.filter_factory.create_filter("command", dict(command="cancel")), self.waiting_for_meet_handling_message),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel)
            ]
        }