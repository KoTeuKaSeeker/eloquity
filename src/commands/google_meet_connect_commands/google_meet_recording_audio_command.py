from typing import List, Dict, Coroutine
from src.commands.google_meet_connect_commands.google_meet_connect_command import GoogleMeetConnectCommand
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from src.google_meet.google_meet_bots_manager import GoogleMeetBotsManager
from src.google_meet.google_meet_bot import GoogleMeetBot
from src.commands.path_transcribe_audio_with_preloaded_names_command import PathTranscribeAudioWithPreloadedNamesCommand
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from telegram import Update, Message, Chat, MessageEntity
from telegram.ext import ContextTypes
from dataclasses import dataclass
import re
import datetime
import pytz
import asyncio
import time
import uuid
import os

WAITING_FOR_AUDIO, WAITING_UNTILL_HANDLING, WAITING_FOR_CONNECTION = range(3)

class GoogleMeetRecordingAudioCommand(GoogleMeetConnectCommand):
    tmp_path: str

    def __init__(self, 
                bots_manager: GoogleMeetBotsManager, 
                dropbox_manager: DropBoxManager, 
                task_extractor: TaskExtractor, 
                transcricribe_request_log_dir: str,
                max_message_waiting_time: datetime.timedelta = datetime.timedelta(minutes=5),
                tmp_path: str = "tmp/"):
        super().__init__(bots_manager, dropbox_manager, task_extractor, transcricribe_request_log_dir, max_message_waiting_time)
        self.transcribe_audio_with_preloaded_names = PathTranscribeAudioWithPreloadedNamesCommand(task_extractor, transcricribe_request_log_dir)
        self.tmp_path = tmp_path

    async def handle_meet(self, update: Update, context: ContextTypes.DEFAULT_TYPE, free_bot: GoogleMeetBot, meet_link: str):
        member_names = free_bot.get_memeber_names()[1:]
        self.transcribe_audio_with_preloaded_names.set_preloaded_names(member_names)

        await update.message.reply_text("🔉 Начата запись аудиопотока конференции... Если вы хотите остановить запись ⛔ и продолжить обработку, выполните команду /stop_recording.")

        audio_name = str(uuid.uuid4())
        audio_path = os.path.join(self.tmp_path, audio_name + ".wav")
        await asyncio.to_thread(free_bot.record_while_on_meet, audio_path)

        free_bot.disconnect()

        await update.message.reply_text("✅ Аудиозапись беседы готова для анализа. Приступаю к распределению задач по участникам встречи... 🧨")
        await update.message.reply_text("Для дебага: участники встречи:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(member_names)]))

        self.transcribe_audio_with_preloaded_names.set_audio_path(audio_path)
        await self.transcribe_audio_with_preloaded_names.handle_command(update, context)

        del self.active_user_handlers[update.message.from_user.id]

        await self.put_update_message("/waiting_untill_handling_continue", update, context)

    async def stop_recording(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⛔ Запись конференции была остановлена. Начинаю анализ записи...")
        if update.message.from_user.id in self.active_user_handlers:
            user_handler: GoogleMeetConnectCommand.UserHandleDiscription = self.active_user_handlers[update.message.from_user.id]
            user_handler.bot.is_recording = False
        

    async def print_bot_end_connection_message(self, update: Update):
        await update.message.reply_text("Бот подключился к конференции 👋")
    
    async def waiting_for_meet_handling_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔖 Бот находится на конференции и записывает её. Если вы хотите остановить запись ⛔ и продолжить обработку, выполните команду /stop_recording. Если вы хотите отменить обработку встречи, выполните команду /cancel.")

    async def waiting_for_connection_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔃 Бот ожидает подключение к встрече... Если хотите отменить обработку встречи, выполните команду /cancel.")

    async def conversation_not_ended_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔃 Аудиозапись обрабатывается... Если хотите отменить обработку встречи, выполните команду /cancel.")

    async def meet_handling_complete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return WAITING_FOR_AUDIO

    def get_telegram_handlers(self) -> List[BaseHandler]:
        return [
            ConversationHandler(
                entry_points=[MessageHandler(filters.Regex(r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}"), self.handle_command)],
                states={
                    WAITING_FOR_CONNECTION: [
                        CommandHandler("waiting_for_connection_continue", self.connection_complete_callback),
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.waiting_for_connection_message)
                    ],
                    WAITING_UNTILL_HANDLING: [
                        CommandHandler("waiting_untill_handling_continue", self.meet_handling_complete_callback),
                        CommandHandler("stop_recording", self.stop_recording),
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.waiting_for_meet_handling_message),
                    ],
                    WAITING_FOR_AUDIO: [
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.conversation_not_ended_message)
                    ]
                },
                fallbacks=[CommandHandler("cancel", self.cancel)])
        ]