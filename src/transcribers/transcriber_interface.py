from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

class TranscriberInterface(ABC):
    
    @dataclass
    class SpeakerData:
        speaker_id: int
        text: str

        def __str__(self):
            return f"speaker_{self.speaker_id}: {self.text}"
        
        def __dict__(self):
            return {
                "speaker_id": self.speaker_id,
                "text": self.text
            }

    
    @dataclass
    class TranscribeResult():
        segments: List["TranscriberInterface.SpeakerData"]

        def __dict__(self):
            return {
                "segments": [{"speaker_id": segment.speaker_id, "text": segment.text} for segment in self.segments]
            }
        
        def __str__(self):
            return "".join(f"{str(segment)}\n" for segment in self.segments)
        
        def __dict__(self) -> dict:
            return [segment.__dict__() for segment in self.segments]

    @abstractmethod
    def transcript_audio(self, file_path: str) -> TranscribeResult:
        pass
