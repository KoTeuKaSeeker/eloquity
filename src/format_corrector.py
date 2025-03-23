import os
from typing import List
from src.exeptions.telegram_exceptions.not_supported_format_exception import NotSupportedFormatException

class FormatCorrector():
    supported_audio_formats: List[str]
    supported_video_formats: List[str]
    
    def __init__(self, supported_audio_formats: List[str], supported_video_formats: List[str]):
        self.supported_audio_formats = supported_audio_formats
        self.supported_video_formats = supported_video_formats
    
    def check_path_format(self, file_path: str):
        extension = os.path.splitext(file_path)[1]
        if extension not in (self.supported_audio_formats + self.supported_video_formats):
            raise NotSupportedFormatException(extension, self.supported_audio_formats, self.supported_video_formats)
        return True