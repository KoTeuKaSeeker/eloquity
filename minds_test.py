from datasets import load_dataset
from datasets import Audio
import librosa

minds = load_dataset("PolyAI/minds14", name="en-AU", split="train", trust_remote_code=True)
minds = minds.cast_column("audio", Audio(sampling_rate=16_000))

from transformers import pipeline

classifier = pipeline(
    "audio-classification",
    model="anton-l/xtreme_s_xlsr_300m_minds14",
)

# example = minds[0]

# print(classifier(example["audio"]["array"]))

audio_path = "data/test_data/audio/audio_1.wav"
audio_array, _ = librosa.load(audio_path, sr=16000)  # sr=16000 ensures it's resampled to 16 kHz

# Prepare the dictionary to match the dataset format
your_audio = {"array": audio_array, "sampling_rate": 16000}

# Now you can use it in the pipeline
print(classifier(your_audio["array"]))