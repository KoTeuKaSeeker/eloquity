import os
from typing import List
from dataclasses import dataclass
from enum import Enum
import whisperx

class AudioTranscriber():
    class WisperSize(Enum):
        TINY = "tiny"
        BASE = "base"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    @dataclass
    class SpeakerData:
        speaker_id: int
        text: str
    
    @dataclass
    class TranscribeResult():
        segments: List["AudioTranscriber.SpeakerData"]

    def __init__(self, 
                 model_size: WisperSize = WisperSize.MEDIUM, 
                 align_model_language: str = "ru",
                 device: str = "cpu", 
                 compute_type: str = "float32"):
        self.wisper_model = whisperx.load_model(model_size.value, device, compute_type=compute_type)
        self.align_model, self.align_metadata = whisperx.load_align_model(language_code=align_model_language, device=device)
        self.diarize_model = whisperx.DiarizationPipeline(device=device)
        self.device = device
        self.compute_type = compute_type
    
    def transcript_audio(self, file_path: str) -> TranscribeResult:
        transcription = self.wisper_model.transcribe(file_path)
        aligned_transcription = whisperx.align(
            transcription["segments"], 
            self.align_model, 
            self.align_metadata, 
            file_path, 
            self.device
        )
        diarization = self.diarize_model(file_path)
        result = whisperx.assign_word_speakers(diarization, aligned_transcription)

        segments: List[AudioTranscriber.SpeakerData] = [AudioTranscriber.SpeakerData(int(segment["speaker"].split("_")[1]), segment["text"]) for segment in result["segments"]]
        transcribe_result: AudioTranscriber.TranscribeResult = AudioTranscriber.TranscribeResult(segments)
        return transcribe_result