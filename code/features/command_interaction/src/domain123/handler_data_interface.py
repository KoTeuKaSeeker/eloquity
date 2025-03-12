from abc import ABC, abstractmethod

class HandlerDataInterface(ABC):
    @abstractmethod
    def get_message_text(self) -> str:
        pass

    @abstractmethod
    def get_message_video_path(self) -> str:
        pass

    @abstractmethod
    def get_message_audio_path(self) -> str:
        pass

    @abstractmethod
    def get_user_data(self) -> dict:
        pass