from src.format_handlers.format_handler_interface import FormatHandlerInterface

class FormatHandler(FormatHandlerInterface):
    audio_dir: str
    audio_extention_to_save: str

    def __init__(self, audio_dir: str, audio_extention_to_save: str):
        self.audio_dir = audio_dir
        self.audio_extention_to_save = audio_extention_to_save
    