import os
import uuid
from typing import List
from telegram import Update
from telegram.ext import ContextTypes
from src.commands.command_interface import CommandInterface
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.ai_exceptions.ai_cant_handle_request_exception import AICantHandleRequestException
from src.task_extractor import TaskExtractor
from telegram.ext._handlers.basehandler import BaseHandler
import logging
import json

class TranscribeAudioCommand(CommandInterface):
    def __init__(self, audio_loader: AudioLoaderInterface, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        self.audio_loader = audio_loader
        self.task_extractor = task_extractor
        self.transcricribe_request_log_dir = transcricribe_request_log_dir

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
            await update.message.reply_text(str(e))
            return

        with open(request_log_path, "w", encoding="utf-8") as file:
            json.dump(json_log, file, indent=2, ensure_ascii=False)
        
        with open(os.path.join(request_log_dir, "transcription.txt"), "w", encoding="utf-8") as file:
            file.write(json_log["replaced_speakers_conversation"])
        
        await update.message.reply_text("✅ Файл готов:")
        await update.message.reply_document(document=open(doc_path, 'rb'))
        logging.info(f"Transcription request complete: {request_id}")
    
    def get_preloaded_names(self) -> List[str]:
        return []