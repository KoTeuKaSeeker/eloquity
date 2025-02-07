from typing import List
import sieve
from src.transcribers.transcriber_interface import TranscriberInterface
import logging

class SieveAudioTranscriber(TranscriberInterface):

    def __init__(self):
        self.word_level_timestamps = True
        self.speaker_diarization = True
        self.speed_boost = False
        self.start_time = 0
        self.end_time = -1
        self.initial_prompt = ""
        self.prefix = ""
        self.language = ""
        self.diarize_min_speakers = -1
        self.diarize_max_speakers = -1
        self.align_only = ""
        self.batch_size = 8
        self.version = "large-v3"

        self.whisperx = sieve.function.get("sieve/whisperx")
    
    def transcript_audio(self, file_path: str) -> TranscriberInterface.TranscribeResult:  
        audio = sieve.File(file_path)
        result = self.whisperx.run(audio, 
                                    self.word_level_timestamps, 
                                    self.speaker_diarization, 
                                    self.speed_boost, 
                                    self.version, 
                                    self.start_time, 
                                    self.end_time, 
                                    self.initial_prompt, 
                                    self.prefix, 
                                    self.language, 
                                    self.diarize_min_speakers, 
                                    self.diarize_max_speakers, 
                                    self.align_only, 
                                    self.batch_size)
        
        segments: List[TranscriberInterface.SpeakerData] = [TranscriberInterface.SpeakerData(int(segment["speaker"].split("_")[1]), segment["text"]) for segment in result["segments"]]
        transcribe_result: TranscriberInterface.TranscribeResult = TranscriberInterface.TranscribeResult(segments)
        return transcribe_result