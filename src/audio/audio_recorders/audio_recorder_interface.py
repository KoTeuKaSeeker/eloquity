from abc import ABC, abstractmethod

class AudioRecorderInterface(ABC):

    @abstractmethod
    def start_record_audio(process_name: str) -> str:
        pass
    
    @abstractmethod
    def stop_record_audio(save_audio_path: str, process_name: str = "") -> str:
        pass