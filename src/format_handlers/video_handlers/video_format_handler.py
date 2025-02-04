import os
from telegram import Update
from typing import List
from src.format_handlers.format_handler import FormatHandler


class VideoFormatHandler(FormatHandler):
    video_dir: str
    audio_extention_to_save: str

    def __init__(self, audio_dir: str, video_dir: str, audio_extention_to_save: str = ".wav"):
        super().__init__(audio_dir, audio_extention_to_save)
        self.video_dir = video_dir
        self.audio_extention_to_save = audio_extention_to_save
