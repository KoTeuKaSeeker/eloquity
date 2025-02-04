from typing import List
from src.exeptions.bot_exception import BotException

class NotSupportedFormatException(BotException):
    not_supported_format: str
    audio_formats: List[str]
    video_formats: List[str]

    def __init__(self, not_supported_format: str, audio_formats: List[str], video_formats: List[str]):
        super().__init__()
        self.not_supported_format = not_supported_format
        self.audio_formats = audio_formats
        self.video_formats = video_formats

        general_message = f'Формат "{self.not_supported_format}" не поддерживается. На данный момент поддерживаются следующие форматы:'
        audio_formats = 'Для аудио: ' + ", ".join(self.audio_formats)
        video_formats =  'Для видео: ' + ", ".join(self.video_formats)
        
        self.error_message = f'{general_message}\n    🔉 {audio_formats}\n    📽️ {video_formats}\n'