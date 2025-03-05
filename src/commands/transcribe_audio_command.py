import os
import uuid
from typing import List
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.commands.command_interface import CommandInterface
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.ai_exceptions.ai_cant_handle_request_exception import AICantHandleRequestException
from src.exeptions.ai_exceptions.gptunnel_required_payment_exception import GptunnelRequiredPaymentException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.bitrix.bitrix_manager import BitrixManager
from src.task_extractor import TaskExtractor
from telegram.ext._handlers.basehandler import BaseHandler
import logging
import json
import requests
import re

SPEAKER_CORRECTION_STATE = range(1)

class TranscribeAudioCommand(CommandInterface):
    class SpeakerCorrectionFilter(filters.BaseFilter):
        def __init__(self):
            super().__init__()

        def filter(self, update: Update) -> bool:
            if not update.message.text:
                return False
            
            text = update.message.text

            


    def __init__(self, audio_loader: AudioLoaderInterface, task_extractor: TaskExtractor, transcricribe_request_log_dir: str, bitrix_manager: BitrixManager):
        self.audio_loader = audio_loader
        self.task_extractor = task_extractor
        self.transcricribe_request_log_dir = transcricribe_request_log_dir
        self.bitrix_manager = bitrix_manager

    async def save_log(self, request_log_path: str, request_log_dir: str, json_log: dict, update: Update, reply_transription: bool = True):
        with open(request_log_path, "w", encoding="utf-8") as file:
            json.dump(json_log, file, indent=2, ensure_ascii=False)
        
        transcription_path = os.path.join(request_log_dir, "transcription.txt")

        with open(transcription_path, "w", encoding="utf-8") as file:
            file.write(json_log["replaced_speakers_conversation"])
            if len(json_log["replaced_speakers_conversation"]) == 0:
                file.write("\n")
        
        if reply_transription:
            await update.message.reply_text("🧑‍💻Дебаг:\n✒️Транскрибация аудиозаписи:")
            await update.message.reply_document(document=open(transcription_path, 'rb'))

    async def format_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            name_dict = context.user_data["name_dict"]
            meet_nicknames = context.user_data["meet_nicknames"]
            speaker_to_user = context.user_data["speaker_to_user"]

            employee_header = "🧑‍💻 Среди всех участников беседы удалось определить, что следующие из них являются сотрудниками компании:"
            company_speakers_list = ""
            not_employee_header = "📌 Также среди участников беседы есть те, кто не является сотрудником компании:"
            not_company_speakers_list = ""
            instruction = "⚔️ Если вы обнаружили, что представленные списки содержат ошибки - отправьте сообщение для корректировки в следующем формате:"
            correction_format = "[сотрудник] speaker_0: Иванов Иван\nspeaker_1: Павлов Владимир\n[сотрудник] speaker_2: Петров Василий\nИ т.д."
            okey_instruction = "✒️ Если всё определно правильно, выполните команду /continue для продолжения обработки."

            identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is not None]
            not_identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is None]
            
            company_speakers_list = "\n".join(f"{speaker}: {name_dict[speaker]} ({meet_nicknames[speaker]})" if speaker in meet_nicknames and meet_nicknames[speaker] is not None else f"{speaker}: {name_dict[speaker]}" for speaker in identified_speakers)
            not_company_speakers_list = "\n".join(f"{speaker}: {name_dict[speaker]} ({meet_nicknames[speaker]})" if speaker in meet_nicknames and meet_nicknames[speaker] is not None else f"{speaker}: {name_dict[speaker]}" for speaker in not_identified_speakers)
            
            message = f"{employee_header}\n{company_speakers_list}\n\n{not_employee_header}\n{not_company_speakers_list}\n\n{instruction}\n{correction_format}\n\n{okey_instruction}"

            await update.message.reply_text(message)

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.chat.send_action("typing")

        request_id = str(uuid.uuid4())
        request_log_dir = os.path.join(self.transcricribe_request_log_dir, request_id)
        request_log_path = os.path.join(request_log_dir, "log.json")
        os.makedirs(request_log_dir, exist_ok=True)

        logging.info(f"New transcription request: {request_id}")
    
        json_log = dict()

        audio_path = await self.audio_loader.load_audio(update, context, json_log, request_log_dir, request_id)
        if audio_path is None:
            return ConversationHandler.END
        await update.message.reply_text("⏮️ Файл был успешно загружен. Идёт обработка звука и анализ текста... 🔃")

        try:
            preloaded_names = self.get_preloaded_names()
            conversation, name_dict, meet_nicknames, speaker_to_user = self.task_extractor.transcirbe_audio_and_identify_names(audio_path, preloaded_names, json_log)

            context.user_data["conversation"] = conversation
            context.user_data["name_dict"] = name_dict
            context.user_data["meet_nicknames"] = meet_nicknames
            context.user_data["speaker_to_user"] = speaker_to_user
            context.user_data["json_log"] = json_log
            context.user_data["request_log_dir"] = request_log_dir
            context.user_data["request_log_path"] = request_log_path
            context.user_data["request_id"] = request_id

            await self.format_message(update, context)

            return SPEAKER_CORRECTION_STATE
        except AICantHandleRequestException as e:
            logging.warning(f"Transcription request failed because the model couldn't assign tasks. Request ID: {request_id}")
            await self.save_log(request_log_path, request_log_dir, json_log, update)
            await update.message.reply_text(str(e))
            return ConversationHandler.END
        except requests.exceptions.HTTPError as e:
            if "402 Client Error: Payment Required for url: " in e.args[0]:
                raise TelegramBotException(GptunnelRequiredPaymentException())

    async def extract_assignee_and_generate_docx_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔃 Идёт извлечение задач из беседы...")

        conversation = context.user_data["conversation"]
        name_dict = context.user_data["name_dict"]
        meet_nicknames = context.user_data["meet_nicknames"]
        speaker_to_user = context.user_data["speaker_to_user"]
        json_log = context.user_data["json_log"]
        request_log_dir = context.user_data["request_log_dir"]
        request_log_path = context.user_data["request_log_path"]
        request_id = context.user_data["request_id"]

        assignees = self.task_extractor.eloquity.identify_assignee_for_participants(conversation, name_dict, meet_nicknames, json_log)
        self.task_extractor.eloquity.add_assignee_to_bitrix(assignees, speaker_to_user, name_dict)
        doc = self.task_extractor.eloquity.generate_docx(conversation, self.task_extractor.docx_template_path, json_log=json_log, assignees=assignees)

        doc_path = os.path.join(request_log_dir, "assignees.docx")
        self.task_extractor.save_doc(doc, doc_path)

        await update.message.reply_text("✅ Файл готов:")
        await self.save_log(request_log_path, request_log_dir, json_log, update)  
        await update.message.reply_document(document=open(doc_path, 'rb'))
        logging.info(f"Transcription request complete: {request_id}")


    async def correct_speakers(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        name_dict = context.user_data["name_dict"]
        meet_nicknames = context.user_data["meet_nicknames"]
        speaker_to_user = context.user_data["speaker_to_user"]

        text = update.message.text
        matches: List[str] = re.findall(r"^(?:\[сотрудник\]\s*)?speaker_\d+:\s*\S+\s+\S+\s*$", text)

        not_found_speakers = {}
        for m in matches:  
            groups = re.match(r"^\s*(\[сотрудник\])?\s*(speaker_\d+):\s*(\S+)\s+(\S+)\s*$", m)
            employee = groups.group(1)
            speaker = groups.group(2)
            last_name = groups.group(3)
            name = groups.group(4)

            if employee is None:
                name_dict[speaker] = f"{last_name} {name}"    
                speaker_to_user[speaker] = None
                continue
            
            users = self.bitrix_manager.find_users(last_name, name)
            if len(users) == 0:
                name_dict[speaker] = f"{last_name} {name}"
                not_found_speakers[speaker] = f"{last_name} {name}"
                continue
            
            user = users[0]
            name_dict[speaker] = f"{user.last_name} {user.name} {user.second_name}"
            speaker_to_user[speaker] = user
        
        if len(not_found_speakers) > 0:
            header = "Среди сотрудников компании не удалось найти следующих участников беседы:"
            users_list = "\n".join(f"{speaker}: {full_name}" for speaker, full_name in not_found_speakers.items())
            instruction = "Возможно вы допустили ошибку в имени - попробуйте ввести ещё раз в том же формате более внимательно. Если же всё корректно - возможно указанных вами участников беседы нет в базе сотрудников компании."

            message = f"{header}\n{users_list}\n\n{instruction}"
            await update.message.reply_text(message)

        await self.format_message(update, context)
        return SPEAKER_CORRECTION_STATE

    async def continue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await self.extract_assignee_and_generate_docx_command(update, context)
        return ConversationHandler.END

    async def wrong_correction_format_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        header = "⏮️ Вы ввели корректирующее сообщение в неверном формате. Используйте следующий формат для корректироваки ошибок при обнаружении имён:"
        format_list = "[сотрудник] speaker_0: Иванов Иван\nspeaker_1: Павлов Владимир\n[сотрудник] speaker_2: Петров Василий\nИ т.д."
        okey_instruction = "✒️ Если всё определно правильно, выполните команду /continue для продолжения обработки."

        message = f"{header}\n{format_list}\n\n{okey_instruction}"
        
        await update.message.reply_text(message)
        return SPEAKER_CORRECTION_STATE

    def get_preloaded_names(self) -> List[str]:
        return []

    def get_telegram_handler(self) -> BaseHandler:
        return ConversationHandler(
            entry_points=[
                    MessageHandler(filters.AUDIO, self.handle_command),
                    MessageHandler(filters.VOICE, self.handle_command),
                    MessageHandler(filters.VIDEO, self.handle_command),
                    MessageHandler(filters.Document.ALL, self.handle_command)
                ],
            states={
                SPEAKER_CORRECTION_STATE: [
                    MessageHandler(filters.Regex(r"^(?:\[сотрудник\]\s*)?speaker_\d+:\s*\S+\s+\S+\s*$"), self.correct_speakers),
                    CommandHandler("continue", self.continue_command),
                    MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.wrong_correction_format_message)
                ],
            },
            fallbacks=[])