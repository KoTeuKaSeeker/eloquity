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

        def __dict__(self):
            return {
                "segments": [{"speaker_id": segment.speaker_id, "text": segment.text} for segment in self.segments]
            }

    @abstractmethod
    def transcript_audio(self, file_path: str) -> TranscribeResult:
        pass
