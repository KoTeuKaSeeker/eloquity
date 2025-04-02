from typing import List, Dict, Coroutine
from src.commands.google_meet_connect_commands.google_meet_connect_command import GoogleMeetConnectCommand
from src.google_meet.google_meet_bots_manager import GoogleMeetBotsManager
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.commands.path_transcribe_audio_with_preloaded_names_command import PathTranscribeAudioWithPreloadedNamesCommand
from src.bitrix.bitrix_manager import BitrixManager
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.file_containers.path_file_container import PathFileContainer
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_handler import MessageHandler
import datetime
import asyncio
import time
import uuid
import os

WAITING_FOR_AUDIO, WAITING_UNTILL_HANDLING, WAITING_FOR_CONNECTION = range(3)

class GoogleMeetRecordingAudioCommand(GoogleMeetConnectCommand):
    tmp_path: str

    def __init__(self, 
                bots_manager: GoogleMeetBotsManager, 
                filter_factory: MessageFilterFactoryInterface,
                max_message_waiting_time: datetime.timedelta = datetime.timedelta(minutes=5),
                tmp_path: str = "tmp/"):
        super().__init__(bots_manager, filter_factory, max_message_waiting_time)
        self.tmp_path = tmp_path
        self.user_id_to_bot = {}

    # async def handle_meet(self, update: Update, context: ContextTypes.DEFAULT_TYPE, free_bot: GoogleMeetBot, meet_link: str):
    #     member_names = free_bot.get_memeber_names()[1:]
    #     context.user_data["preloaded_names"] = member_names

    #     await update.message.reply_text("🔉 Начата запись аудиопотока конференции... Если вы хотите остановить запись ⛔ и продолжить обработку, выполните команду /stop_recording.")

    #     audio_name = str(uuid.uuid4())
    #     audio_path = os.path.join(self.tmp_path, audio_name + ".wav")

    #     free_bot.disconnect()

    #     await update.message.reply_text("✅ Аудиозапись беседы готова для анализа. Приступаю к распределению задач по участникам встречи... 🧨")
    #     await update.message.reply_text("Для дебага: участники встречи:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(member_names)]))

    #     context.user_data["preloaded_audio_path"] = audio_path
    #     # await self.transcribe_audio_with_preloaded_names.handle_command(update, context)

    #     del self.active_user_handlers[update.message.from_user.id]

    #     # await self.put_update_message("/waiting_untill_handling_continue", update, context)
    #     await self.put_update_message("/start_transcribator", update, context)

    #     time.sleep(3)
        
    #     await self.put_update_message("/start_transcribator", update, context)

    async def handle_meet(self, bot: GoogleMeetBot, audio_path: str):
        await asyncio.to_thread(bot.record_while_on_meet, audio_path)

        bot.disconnect()

    async def print_okay_message(self, member_names: List[str], chat: ChatInterface):
        await chat.send_message_to_query("🔉 Начата запись аудиопотока конференции... Если вы хотите остановить запись ⛔ и продолжить обработку, выполните команду /stop_recording.")

    async def after_handling_meet(self, free_bot, message: dict, context: dict, chat: ChatInterface):
        audio_name = str(uuid.uuid4())
        audio_path = os.path.join(self.tmp_path, audio_name + ".wav")
        context["chat_data"]["audio_path"] = audio_path

        asyncio.create_task(self.handle_meet(free_bot, audio_path))

        self.user_id_to_bot[context["user_id"]] = free_bot

    async def handle_command(self, message: dict, context: dict, chat: ChatInterface) -> str:
        await super().handle_command(message, context, chat)
        return chat.move_next(context, "google_meet_waiting_stop_recording", "entry_point")

    async def stop_recording(self, message: dict, context: dict, chat: ChatInterface) -> str:
        await chat.send_message_to_query("⛔ Запись конференции была остановлена. Для продолжения анализа записи выполните команду /continue")
        if context["user_id"] in self.user_id_to_bot:
            self.user_id_to_bot[context["user_id"]].is_recording = False

        while not os.path.exists(context["chat_data"]["audio_path"]): await asyncio.sleep(1)

        message = {"audio_container": PathFileContainer(context["chat_data"]["audio_path"])}
        # await chat.move_next_and_send_message_to_event_loop("message_transcribe_audio_with_preloaded_names_command", "entry_point", message, context, chat)
        return chat.move_next(context, "message_transcribe_audio_with_preloaded_names_command", "entry_point")

    # async def print_bot_end_connection_message(self, update: Update):
    #     await update.message.reply_text("Бот подключился к конференции 👋")
    
    # async def waiting_for_meet_handling_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #     await update.message.reply_text("🔖 Бот находится на конференции и записывает её. Если вы хотите остановить запись ⛔ и продолжить обработку, выполните команду /stop_recording. Если вы хотите отменить обработку встречи, выполните команду /cancel.")

    # async def waiting_for_connection_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #     await update.message.reply_text("🔃 Бот ожидает подключение к встрече... Если хотите отменить обработку встречи, выполните команду /cancel.")

    # async def conversation_not_ended_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #     await update.message.reply_text("🔃 Аудиозапись обрабатывается... Если хотите отменить обработку встречи, выполните команду /cancel.")

    # async def start_transcribator_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     return move_next(context, ConversationState.waiting, ConversationState.waiting)

    # def get_conversation_states(self) -> Dict[str, BaseHandler]:
    #     return {
    #         ConversationState.waiting: [
    #             MessageHandler(filters.Regex(r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}"), self.handle_command)
    #         ],
    #         ConversationState.google_meet_waiting_for_connection: [
    #             CommandHandler("waiting_for_connection_continue", self.connection_complete_callback),
    #             MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.waiting_for_connection_message),
    #             CommandHandler("cancel", self.cancel)
    #         ],
    #         ConversationState.google_meet_waiting_untill_handling: [
    #             CommandHandler("start_transcribator", self.start_transcribator_callback),
    #             MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.waiting_for_meet_handling_message),
    #             CommandHandler("cancel", self.cancel)
    #         ]
    #     }

    def get_conversation_states(self) -> Dict[str, List[MessageHandler]]: 
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}")), self.handle_command)
            ],
            "google_meet_waiting_stop_recording": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="stop_recording")), self.stop_recording),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel),
                MessageHandler(self.filter_factory.create_filter("all"), self.conversation_not_ended_message),
            ]
        }