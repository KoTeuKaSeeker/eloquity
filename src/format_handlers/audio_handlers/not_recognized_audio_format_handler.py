import os
from typing import List
from telegram import Update
from pydub import AudioSegment
from src.format_handlers.audio_handlers.audio_format_handler import AudioFormatHandler
from src.exeptions.not_supported_format_exception import NotSupportedFormatException

class NotRecognizedAudioFormatHandler(AudioFormatHandler):
    extentions: List[str]
    
    def __init__(self, audio_dir: str, audio_extention_to_save: str, extentions: List[str]):
        super().__init__(audio_dir, audio_extention_to_save)
        self.extentions = extentions

    async def load_audio(self, update: Update, context) -> str:
        if update.message.document:
            file = await update.message.document.get_file()
            file_name = update.message.document.file_name
            file_ext = os.path.splitext(file_name)[1].lower()

            if file_ext in self.extentions:
                file_path = os.path.join(self.audio_dir, file_name)
                await file.download_to_drive(file_path)
                
                changed_extention_path = os.path.splitext(file_path)[0] + self.audio_extention_to_save
                audio_segment = AudioSegment.from_file(file_path)
                audio_segment.export(changed_extention_path, format=self.audio_extention_to_save.lstrip("."))

                if file_path != changed_extention_path:
                    os.remove(file_path)

                return changed_extention_path
            else:
                from src.format_handlers_manager import allow_audio_extentions, allow_video_extentions
                raise NotSupportedFormatException(file_ext, allow_audio_extentions, allow_video_extentions)
        else:
            return None
