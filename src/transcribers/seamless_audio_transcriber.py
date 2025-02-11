import torchaudio
from typing import List
from transformers import AutoProcessor, SeamlessM4Tv2Model
from src.transcribers.transcriber_interface import TranscriberInterface

class SeamlessAudioTranscriber(TranscriberInterface):

    def __init__(self, 
                 device: str = "cpu"):
        self.processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
        self.model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large").to(device)
        self.device = device
    
    def transcript_audio(self, file_path: str) -> TranscriberInterface.TranscribeResult:
        audio, orig_freq =  torchaudio.load(file_path)
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
        audio_inputs = self.processor(audios=audio, return_tensors="pt")
        audio_inputs["input_features"] = audio_inputs["input_features"].to(self.device)
        audio_inputs["attention_mask"] = audio_inputs["attention_mask"].to(self.device)

        tokens = self.model.generate(**audio_inputs, tgt_lang="rus", generate_speech=False)[0].cpu().numpy().squeeze()
        text = self.processor.tokenizer.decode(tokens, skip_special_tokens=True)


        segments: List[TranscriberInterface.SpeakerData] = [TranscriberInterface.SpeakerData(int(0), text)]
        transcribe_result: TranscriberInterface.TranscribeResult = TranscriberInterface.TranscribeResult(segments)
        return transcribe_result