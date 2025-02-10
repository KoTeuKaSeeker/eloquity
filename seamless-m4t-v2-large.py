from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio

processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")

# from audio
audio, orig_freq =  torchaudio.load(r"data\test_data\audio\audio_1.wav")
audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
audio_inputs = processor(audios=audio, return_tensors="pt")
text = model.generate(**audio_inputs, tgt_lang="rus", generate_speech=False)[0].cpu().numpy().squeeze()
text = processor.tokenizer.decode(text, skip_special_tokens=True)
