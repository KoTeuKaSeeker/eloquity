import torch
import librosa
import torchaudio
from datasets import load_dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

LANG_ID = "ru"
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
SAMPLES = 5

audio_file_path = r"data\test_data\audio\audio_1.wav"


processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

y, sr = librosa.load(audio_file_path, sr=16000)  # Принудительно приводим к 16kHz
inputs = processor(y, sampling_rate=16_000, return_tensors="pt", padding=True)

with torch.no_grad():
    logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

predicted_ids = torch.argmax(logits, dim=-1)
predicted_sentences = processor.batch_decode(predicted_ids)

for i, predicted_sentence in enumerate(predicted_sentences):
    print("-" * 100)
    print("Prediction:", predicted_sentence)