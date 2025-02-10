import os
import torch
import librosa
from typing import List
from datasets import load_dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from src.transcribers.transcriber_interface import TranscriberInterface

class FacebookWisperTranscriber(TranscriberInterface):

    def __init__(self, 
                 device: str = "cpu"):
        LANG_ID = "ru"
        MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
        SAMPLES = 5

        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
        self.model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(device)
        self.device = device
    
    def transcript_audio(self, file_path: str) -> TranscriberInterface.TranscribeResult:
        y, _ = librosa.load(file_path, sr=16_000)
        inputs = self.processor(y, sampling_rate=16_000, return_tensors="pt", padding=True)
        inputs.input_values = inputs.input_values.to(self.device)
        inputs.attention_mask = inputs.attention_mask.to(self.device)

        with torch.no_grad():
            logits = self.model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_sentences = self.processor.batch_decode(predicted_ids)

        segments: List[TranscriberInterface.SpeakerData] = [TranscriberInterface.SpeakerData(int(0), sentence) for sentence in predicted_sentences]
        transcribe_result: TranscriberInterface.TranscribeResult = TranscriberInterface.TranscribeResult(segments)
        return transcribe_result
    