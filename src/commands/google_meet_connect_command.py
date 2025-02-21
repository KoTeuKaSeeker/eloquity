from typing import List
from src.commands.command_interface import CommandInterface
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from src.google_meet.google_meet_bots_manager import GoogleMeetBotsManager
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from telegram import Update
from telegram.ext import ContextTypes
import re
import datetime
import pytz

WAITING_FOR_AUDIO = 0

class GoogleMeetConnectCommand(CommandInterface):
    bots_manager: GoogleMeetBotsManager

    def __init__(self, 
                bots_manager: GoogleMeetBotsManager, 
                dropbox_manager: DropBoxManager, 
                task_extractor: TaskExtractor, 
                transcricribe_request_log_dir: str, 
                max_message_waiting_time: datetime.timedelta = datetime.timedelta(minutes=5)):
        self.bots_manager = bots_manager
        self.transcribe_audio_with_preloaded_names = TranscribeAudioWithPreloadedNamesCommand(dropbox_manager, task_extractor, transcricribe_request_log_dir)
        self.max_message_waiting_time = max_message_waiting_time

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        pattern = r"(?:https:\/\/)?meet\.google\.com\/[a-z]{3}-[a-z]{4}-[a-z]{3}"
        if len(re.findall(pattern, text)) > 0:
            message_date = update.message.forward_origin.date if update.message.forward_origin else update.message.date
            message_waiting_time = datetime.datetime.now(pytz.UTC) - message_date

            if message_waiting_time > self.max_message_waiting_time:
                all_minutes, seconds = divmod(message_waiting_time.seconds, 60)
                hours, minutes = divmod(all_minutes, 60)
                days = message_waiting_time.days
                
                await update.message.reply_text(f"⏮️ Прошло слишком много времени с момента отправки приглашения на встречу ({days} дн. {hours} ч. {minutes} мин.), возможно встреча уже закончилась.\n❄️ Если это не так, пожалуйста, отправьте приглашение на встречу заново (не перессылкой, а новым сообщением).")
                return ConversationHandler.END

            await update.message.reply_text("Ссылка на Google Meet встречу была обнаружена. Подключаюсь к конференции... 🔃")
            
            free_bot = await self.bots_manager.connect_bot(text)
            if free_bot is None:
                await update.message.reply_text("⏮️ Не могу подключиться к конференции, так как все Google Meet боты заняты. Повторите попытку позже.")
                return ConversationHandler.END
            
            member_names = await free_bot.get_memeber_names()[1:]

            await update.message.reply_text("✅ Обработка информации встречи завершена. Когда будете готовы, отравьте аудиозапись беседы со встречи следующим сообщением.\nЕсли же вы хотите завершить обработку встречи, выполните команду /cancel.")
            await update.message.reply_text("Для дебага: участники встречи:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(member_names)]))

            self.transcribe_audio_with_preloaded_names.set_preloaded_names(member_names)

            free_bot.disconnect()

            return WAITING_FOR_AUDIO
        return ConversationHandler.END
    
    async def conversation_not_ended_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("⏮️ Пожалуйста, отправьте аудиозапись беседы со встречи 🔉. Если хотите отменить обработку встречи, выполните команду /cancel.")
        return WAITING_FOR_AUDIO

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔖 Обработка встречи отменена.")
        return ConversationHandler.END

    def get_telegram_handlers(self) -> List[BaseHandler]:
        return [
            ConversationHandler(
                entry_points=[MessageHandler(filters.TEXT, self.handle_command)],
                states={
                    WAITING_FOR_AUDIO: [
                        MessageHandler(filters.AUDIO | filters.VOICE | filters.VIDEO, self.transcribe_audio_with_preloaded_names.handle_command),
                        MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.conversation_not_ended_message)
                        ]
                },
                fallbacks=[CommandHandler("cancel", self.cancel)]
            )
        ]