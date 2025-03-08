import os
import uuid
from typing import List, Dict
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.commands.command_interface import CommandInterface
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.ai_exceptions.ai_cant_handle_request_exception import AICantHandleRequestException
from src.exeptions.ai_exceptions.gptunnel_required_payment_exception import GptunnelRequiredPaymentException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.AI.eloquity_ai import Assignee
from src.bitrix.bitrix_manager import BitrixManager
from src.task_extractor import TaskExtractor
from telegram.ext._handlers.basehandler import BaseHandler
import logging
import json
import requests
import re
from src.conversation.conversation_states_manager import ConversationState, move_next, move_back

SPEAKER_CORRECTION_STATE = range(1)

class TranscribeAudioCommand(CommandInterface):
    class SpeakerCorrectionFilter(filters.MessageFilter):
        def __init__(self, pattern: str):
            super().__init__()
            self.pattern = pattern

        def filter(self, message) -> bool:
            for line in message.text.split("\n"):
                if not re.match(self.pattern, line):
                    return False
            return True

    def __init__(self, audio_loader: AudioLoaderInterface, task_extractor: TaskExtractor, transcricribe_request_log_dir: str, bitrix_manager: BitrixManager, speaker_correction_state: ConversationState):
        self.audio_loader = audio_loader
        self.task_extractor = task_extractor
        self.transcricribe_request_log_dir = transcricribe_request_log_dir
        self.bitrix_manager = bitrix_manager
        self.speaker_correction_state = speaker_correction_state

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
            speaker_to_user = context.user_data["speaker_to_user"]

            employee_header = "🧑‍💻 Участники беседы, которые являются членами компании:"
            company_speakers_list = ""
            not_employee_header = "📌 Участники беседы, которые не являтся членами компании:"
            not_company_speakers_list = ""
            instruction = "⚔️ Если вы обнаружили, что представленные списки содержат ошибки - отправьте сообщение для корректировки в следующем формате:"
            correction_format = "1. Иван Иванов [сотрудник]\n2. Владимир Павлов\n5. Василий Петров [сотрудник]\nИ т.д."
            okey_instruction = "✒️ Если всё определно правильно, выполните команду /continue для продолжения обработки. Если хотите отменить обработку - выполните команду /cancel."

            identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is not None]
            not_identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is None]
            
            company_speakers_list = "\n".join(f"{i+1}. {speaker}"  for i, speaker in enumerate(identified_speakers))
            not_company_speakers_list = "\n".join(f"{len(identified_speakers) + i+1}. {speaker}"  for i, speaker in enumerate(not_identified_speakers))
            
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
            return move_back(context)
        await update.message.reply_text("⏮️ Файл был успешно загружен. Идёт обработка звука и анализ текста... 🔃")

        try:
            
            preloaded_names = context.user_data["preloaded_names"] if "preloaded_names" in context.user_data else []
            conversation = self.task_extractor.transcribe_audio(audio_path, json_log)
            assignees = self.task_extractor.eloquity.generate_assignees(conversation, json_log, preloaded_names)
            speaker_to_user = self.task_extractor.eloquity.correct_assignees_with_bitirx(assignees)

            context.user_data["preloaded_names"] = []

            context.user_data["assignees"] = assignees
            context.user_data["speaker_to_user"] = speaker_to_user
            context.user_data["json_log"] = json_log
            context.user_data["request_log_dir"] = request_log_dir
            context.user_data["request_log_path"] = request_log_path
            context.user_data["request_id"] = request_id

            await self.format_message(update, context)

            return move_next(context, self.speaker_correction_state, ConversationState.waiting)
        except AICantHandleRequestException as e:
            logging.warning(f"Transcription request failed because the model couldn't assign tasks. Request ID: {request_id}")
            await self.save_log(request_log_path, request_log_dir, json_log, update)
            await update.message.reply_text(str(e))
            return move_back(context)
        except requests.exceptions.HTTPError as e:
            if "402 Client Error: Payment Required for url: " in e.args[0]:
                raise TelegramBotException(GptunnelRequiredPaymentException())

    async def extract_assignee_and_generate_docx_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔃 Идёт извлечение задач из беседы...")

        assignees = context.user_data["assignees"]
        json_log = context.user_data["json_log"]
        request_log_dir = context.user_data["request_log_dir"]
        request_log_path = context.user_data["request_log_path"]
        request_id = context.user_data["request_id"]

        doc = self.task_extractor.eloquity.get_docx_from_assignees(assignees, self.task_extractor.docx_template_path)

        doc_path = os.path.join(request_log_dir, "assignees.docx")
        self.task_extractor.save_doc(doc, doc_path)

        await update.message.reply_text("✅ Файл готов:")
        await self.save_log(request_log_path, request_log_dir, json_log, update)  
        await update.message.reply_document(document=open(doc_path, 'rb'))
        logging.info(f"Transcription request complete: {request_id}")


    async def correct_speakers(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        assignees: List[Assignee] = context.user_data["assignees"]
        speaker_to_user = context.user_data["speaker_to_user"]

        text = update.message.text
        matches: List[str] = re.findall(r"^\d+.\s*\S+\s+\S+\s*(?:\[сотрудник\])?\s*$", text, re.DOTALL | re.MULTILINE)

        speaker_to_assignee = {assignee.original_speaker_name: assignee for assignee in assignees}
        identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is not None]
        not_identified_speakers = [speaker for speaker, user in speaker_to_user.items() if user is None]
        ordered_speakers = identified_speakers + not_identified_speakers

        not_found_speakers = {}
        for m in matches:  
            groups = re.match(r"^(\d+).\s*(\S+)\s+(\S+)\s*(\[сотрудник\])?\s*$", m)
            speaker_id = int(groups.group(1)) - 1
            name = groups.group(2)
            last_name = groups.group(3)
            employee = groups.group(4)

            if speaker_id < 0 or speaker_id >= len(ordered_speakers):
                await update.message.reply_text(f'🎃 Вы указали участника "{speaker_id+1}. {name} {last_name}" под номером {speaker_id+1}, хотя номер должен лежать в диапазоне [1, {len(ordered_speakers)}]. Повторите попытку, указав верный номер.')
                return move_next(context, self.speaker_correction_state, ConversationState.waiting)

            speaker = ordered_speakers[speaker_id]
            user = speaker_to_user[speaker]
            assignee = speaker_to_assignee[speaker]

            if employee is None:
                assignee.original_speaker_name = f"{name} {last_name}" 
                assignee.name = assignee.original_speaker_name
                del speaker_to_user[speaker]
                speaker_to_user[assignee.original_speaker_name] = None
                continue
            
            users = self.bitrix_manager.find_users(last_name, name)
            if len(users) == 0:
                assignee.original_speaker_name = f"{name} {last_name}" 
                assignee.name = assignee.original_speaker_name
                not_found_speakers[speaker_id] = f"{name} {last_name}"
                del speaker_to_user[speaker]
                speaker_to_user[assignee.original_speaker_name] = user
                continue
            
            user = users[0]
            assignee.original_speaker_name = f"{user.name} {user.second_name} {user.last_name}"
            assignee.name = assignee.original_speaker_name

            del speaker_to_user[speaker]
            speaker_to_user[assignee.original_speaker_name] = user
        
        if len(not_found_speakers) > 0:
            header = "💀 Следующих участников беседы не удалось найти среди сотрудников компании:"
            users_list = "\n".join(f"{speaker_id + 1}. {full_name}" for speaker_id, full_name in not_found_speakers.items())
            instruction = "✒️ Возможно вы допустили ошибку в имени - попробуйте ввести ещё раз в том же формате более внимательно 😉. Если же всё корректно - возможно указанных вами участников беседы нет в базе сотрудников компании."

            message = f"{header}\n{users_list}\n\n{instruction}"
            await update.message.reply_text(message)

        await self.format_message(update, context)
        return move_next(context, self.speaker_correction_state, ConversationState.waiting)

    async def continue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        assignees = context.user_data["assignees"]
        speaker_to_user = context.user_data["speaker_to_user"]
        self.task_extractor.eloquity.add_assignee_to_bitrix(assignees, speaker_to_user)

        await self.extract_assignee_and_generate_docx_command(update, context)
        return move_back(context)

    async def wrong_correction_format_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        header = "⏮️ Вы ввели корректирующее сообщение в неверном формате. Используйте следующий формат для корректироваки ошибок при обнаружении имён:"
        format_list = "1. Иван Иванов [сотрудник]\n2. Владимир Павлов\n5. Василий Петров [сотрудник]\nИ т.д."
        okey_instruction = "✒️ Если вы хотите продолжить обработку без корректировок, выполните команду /continue. Если хотите отменить обработку - выполните команду /cancel."

        message = f"{header}\n{format_list}\n\n{okey_instruction}"
        
        await update.message.reply_text(message)
        return move_next(context, self.speaker_correction_state, ConversationState.waiting)

    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("🔖 Обработка аудиозаписи отменена.")
        return move_back(context)

    def get_conversation_states(self) -> Dict[str, BaseHandler]:
        return {
            ConversationState.waiting: [
                MessageHandler(filters.AUDIO, self.handle_command),
                MessageHandler(filters.VOICE, self.handle_command),
                MessageHandler(filters.VIDEO, self.handle_command),
                MessageHandler(filters.Document.ALL, self.handle_command)
            ],
            self.speaker_correction_state: [
                MessageHandler(TranscribeAudioCommand.SpeakerCorrectionFilter(r"^\d+.\s*\S+\s+\S+\s*(?:\[сотрудник\])?\s*$"), self.correct_speakers),
                CommandHandler("continue", self.continue_command),
                MessageHandler(~filters.Regex(r"^/cancel(?:@\w+)?\b"), self.wrong_correction_format_message),
                CommandHandler("cancel", self.cancel_command)
            ]
        }