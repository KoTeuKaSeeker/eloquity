from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

class TranscriberInterface(ABC):
    
    @dataclass
    class SpeakerData:
        speaker_id: int
        text: str
    
    @dataclass
    class TranscribeResult():
        segments: List["TranscriberInterface.SpeakerData"]

    @abstractmethod
    def transcript_audio(self, file_path: str) -> TranscribeResult:
        pass
