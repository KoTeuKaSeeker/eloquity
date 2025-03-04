import os
import uuid
from typing import List
from telegram import Update
from telegram.ext import ContextTypes
from src.commands.command_interface import CommandInterface
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.ai_exceptions.ai_cant_handle_request_exception import AICantHandleRequestException
from src.exeptions.ai_exceptions.gptunnel_required_payment_exception import GptunnelRequiredPaymentException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.task_extractor import TaskExtractor
from telegram.ext._handlers.basehandler import BaseHandler
import logging
import json
import requests

class TranscribeAudioCommand(CommandInterface):
    def __init__(self, audio_loader: AudioLoaderInterface, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        self.audio_loader = audio_loader
        self.task_extractor = task_extractor
        self.transcricribe_request_log_dir = transcricribe_request_log_dir

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
            return
        await update.message.reply_text("⏮️ Файл был успешно загружен. Идёт обработка звука и анализ текста... 🔃")

        try:
            preloaded_names = self.get_preloaded_names()
            doc_path = self.task_extractor.extract_and_save_tasks(audio_path, preloaded_names=preloaded_names, json_log=json_log)
        except AICantHandleRequestException as e:
            logging.warning(f"Transcription request failed because the model couldn't assign tasks. Request ID: {request_id}")
            await self.save_log(request_log_path, request_log_dir, json_log, update)
            await update.message.reply_text(str(e))
            return
        except requests.exceptions.HTTPError as e:
            if "402 Client Error: Payment Required for url: " in e.args[0]:
                raise TelegramBotException(GptunnelRequiredPaymentException())
                

        await update.message.reply_text("✅ Файл готов:")
        await self.save_log(request_log_path, request_log_dir, json_log, update)  
        await update.message.reply_document(document=open(doc_path, 'rb'))
        logging.info(f"Transcription request complete: {request_id}")
    
    def get_preloaded_names(self) -> List[str]:
        return []