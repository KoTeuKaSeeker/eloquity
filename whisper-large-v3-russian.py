import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline
from io import BytesIO
import torchaudio

torch_dtype = torch.bfloat16 # set your preferred type here 

device = 'cpu'
if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'
    setattr(torch.distributed, "is_initialized", lambda : False) # monkey patching
device = torch.device(device)

whisper = WhisperForConditionalGeneration.from_pretrained(
    "antony66/whisper-large-v3-russian", torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True,
    # add attn_implementation="flash_attention_2" if your GPU supports it
)

processor = WhisperProcessor.from_pretrained("antony66/whisper-large-v3-russian")

asr_pipeline = pipeline(
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

# read your wav file into variable wav. For example:
# wav = BytesIO()
# with open('data/test_data/audio/audio_1.wav', 'rb') as f:
#     wav.write(f.read())
# wav.seek(0)

# waveform, sample_rate = torchaudio.load(wav)
# waveform = waveform.mean(dim=0, keepdim=True).numpy()

import librosa
audio_path = "data/test_data/audio/audio_1.wav"
audio_array, _ = librosa.load(audio_path, sr=16000) 
your_audio = {"array": audio_array, "sampling_rate": 16000}


# get the transcription
asr = asr_pipeline(your_audio, generate_kwargs={"language": "russian", "max_new_tokens": 256}, return_timestamps=False)

print(asr['text'])
