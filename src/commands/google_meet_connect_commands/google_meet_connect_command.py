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
                filter_factory: MessageFilterFactoryInterface,
                max_message_waiting_time: datetime.timedelta = datetime.timedelta(minutes=5),
                ):
        self.bots_manager = bots_manager
        self.max_message_waiting_time = max_message_waiting_time
        self.active_user_handlers = {}
        self.filter_factory = filter_factory

    async def handle_command(self, message: dict, context: dict, chat: ChatInterface) -> str:
        meet_link = message["text"]
        message_date = message["forward_origin_date"] if "forward_origin_date" in message else message["date"]
        message_waiting_time = datetime.datetime.now(pytz.UTC) - message_date

        if message_waiting_time > self.max_message_waiting_time:
            all_minutes, seconds = divmod(message_waiting_time.seconds, 60)
            hours, minutes = divmod(all_minutes, 60)
            days = message_waiting_time.days
            
            await chat.send_message_to_query(f"⏮️ Прошло слишком много времени с момента отправки приглашения на встречу ({days} дн. {hours} ч. {minutes} мин.), возможно встреча уже закончилась.\n❄️ Если это не так, пожалуйста, отправьте приглашение на встречу заново (не перессылкой, а новым сообщением).")
            return chat.move_back(context)

        free_bot = self.bots_manager.get_free_bot()

        if free_bot is None:
            await chat.send_message_to_query("⏮️ Не могу подключиться к конференции, так как все Google Meet боты заняты. Повторите попытку позже.")
            return chat.move_back(context)

        is_call_accept = free_bot.connect_to_meet(meet_link, max_page_loading_time=60, max_accept_call_time=60)

        if not is_call_accept:
            await chat.send_message_to_query("⏮️ Истекло время ожидания подключения к конференции (60 секунд).")
            free_bot.disconnect()
            return chat.move_back(context)

        member_names = free_bot.get_memeber_names(open_members_menu_time=60)[1:]
        context["user_data"]["preloaded_names"] = member_names

        await chat.send_message_to_query("✅ Обработка информации встречи завершена. Когда будете готовы, отравьте аудиозапись беседы со встречи следующим сообщением.\nЕсли же вы хотите завершить обработку встречи, выполните команду /cancel.")
        await chat.send_message_to_query("Для дебага: участники встречи:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(member_names)]))

        free_bot.disconnect()

        return chat.move_next(context, "google_meet_waiting_for_audio", "entry_point")

    async def handle_audio(self, message: dict, context: dict, chat: ChatInterface) -> str:
        return await chat.move_next_and_send_message_to_event_loop("message_transcribe_audio_with_preloaded_names_command", "entry_point", message, context, chat)

    async def conversation_not_ended_message(self, message: dict, context: dict, chat: ChatInterface) -> str:
        await chat.send_message_to_query("⏮️ Пожалуйста, отправьте аудиозапись со встречи 🔖. Если хотите отменить обработку встречи, выполните команду /cancel.")
        return chat.stay_on_state(context)

    async def cancel(self, message: dict, context: dict, chat: ChatInterface) -> str:
        await chat.send_message_to_query("🔖 Обработка встречи отменена.")
        return chat.move_back(context)

    # async def print_bot_end_connection_message(self, update: Update):
    #     await update.message.reply_text("Бот подключился к конференции 👋")

    # async def waiting_for_connection_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #     await update.message.reply_text("🔃 Бот ожидает подключение к встрече... Если хотите отменить обработку встречи, выполните команду /cancel.")
    
    # async def waiting_for_meet_handling_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #     await update.message.reply_text("📅 Бот находится на конференции и анализирует её. Если хотите отменить обработку встречи, выполните команду /cancel.")

    # async def connection_complete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     return move_next(context, ConversationState.google_meet_waiting_untill_handling, ConversationState.waiting)
    
    # async def meet_handling_complete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     return move_next(context, ConversationState.message_speaker_correction_state_with_preloaded_names, ConversationState.waiting)

    def get_conversation_states(self) -> Dict[str, MessageHandler]: 
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}")), self.handle_command)
            ],
            "google_meet_waiting_for_audio": [
                MessageHandler(self.filter_factory.create_filter("audio"), self.handle_audio),
                MessageHandler(self.filter_factory.create_filter("voice"), self.handle_audio),
                MessageHandler(self.filter_factory.create_filter("video"), self.handle_audio),
                MessageHandler(self.filter_factory.create_filter("document.all"), self.handle_audio),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel),
                MessageHandler(self.filter_factory.create_filter("all"), self.conversation_not_ended_message),
            ],
        }