from src.domain.handler_data_interface import HandlerDataInterface

class HandlerData(HandlerDataInterface):
    text: str
    video_path: str
    audio_path: str
    user_data: dict

    def __init__(self, text: str = None, video_path: str = None, audio_path: str = None, user_data: dict = None):
        self.text = text
        self.video_path = video_path
        self.audio_path = audio_path
        self.user_data = user_data

    def get_message_text(self) -> str:
        return self.text

    def get_message_video_path(self) -> str:
        return self.video_path

    def get_message_audio_path(self) -> str:
        return self.audio_path

    def get_user_data(self) -> dict:
        return self.user_data