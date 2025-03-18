from typing import List
from telegram import Message
from src.format_handlers.format_handler_interface import FormatHandlerInterface
from src.format_handlers.audio_handlers.recognized_audio_format_handler import RecognizedAudioFormatHandler
from src.format_handlers.audio_handlers.not_recognized_audio_format_handler import NotRecognizedAudioFormatHandler
from src.format_handlers.video_handlers.recognized_video_format_handler import RecognizedVideoFormatHandler

allow_audio_extentions: List[str] = [".mp3", ".wav", ".m4a"]
allow_video_extentions: List[str] = [".mp4", ".mov"]

class FormatHandlersManager(FormatHandlerInterface):
    recognized_audio_format_handler: RecognizedAudioFormatHandler
    not_recognized_audio_format_handler: NotRecognizedAudioFormatHandler
    recognized_video_format_handler: RecognizedVideoFormatHandler
    handlers: List[FormatHandlerInterface]

    def __init__(self, audio_dir: str, video_dir: str, audio_extention_to_save: str = ".mp3"):
        self.recognized_audio_format_handler = RecognizedAudioFormatHandler(audio_dir, audio_extention_to_save)
        self.not_recognized_audio_format_handler = NotRecognizedAudioFormatHandler(audio_dir, audio_extention_to_save, allow_audio_extentions)
        self.recognized_video_format_handler = RecognizedVideoFormatHandler(audio_dir, video_dir, audio_extention_to_save)
        self.handlers = [
            self.recognized_audio_format_handler,
            self.not_recognized_audio_format_handler,
            self.recognized_video_format_handler,
        ]
    
    async def load_audio(self, message: Message) -> str:
        for handler in self.handlers:
            result = await handler.load_audio(message)
            if result is not None:
                return result
                
                
    
        