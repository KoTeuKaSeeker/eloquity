from typing import List
import sieve
from src.transcribers.transcriber_interface import TranscriberInterface
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline
import torch
import librosa


class AntonyWhisperTranscriber(TranscriberInterface):

    def __init__(self, device: str):
        torch_dtype = torch.bfloat16
        whisper = WhisperForConditionalGeneration.from_pretrained(
            "antony66/whisper-large-v3-russian", torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
        
        processor = WhisperProcessor.from_pretrained("antony66/whisper-large-v3-russian")

        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=whisper,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=256,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )
    
    def transcript_audio(self, file_path: str) -> TranscriberInterface.TranscribeResult:  
        audio_array, _ = librosa.load(file_path, sr=16000) 
        audio = {"array": audio_array, "sampling_rate": 16000}

        result = self.asr_pipeline(audio, generate_kwargs={"language": "russian", "max_new_tokens": 256}, return_timestamps=False)
        
        segments: List[TranscriberInterface.SpeakerData] = [TranscriberInterface.SpeakerData(0, result['text'])]
        transcribe_result: TranscriberInterface.TranscribeResult = TranscriberInterface.TranscribeResult(segments)
        return transcribe_result