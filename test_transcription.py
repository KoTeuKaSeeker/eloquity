from src.transcribers.audio_transcriber import AudioTranscriber
from src.transcribers.sieve_audio_transcriber import SieveAudioTranscriber
from src.transcribers.antony_whisper_trainscriber import AntonyWhisperTranscriber
from src.transcribers.facebook_wisper_transcriber import FacebookWisperTranscriber
from src.transcribers.seamless_audio_transcriber import SeamlessAudioTranscriber
import os
import time
import json
from pydub import AudioSegment
import torch


if __name__ == "__main__":
    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda'
    elif torch.backends.mps.is_available():
        device = 'mps'
        setattr(torch.distributed, "is_initialized", lambda : False) # monkey patching
    device = torch.device(device)

    audio_dir = "data/test_data/audio"
    result_dir = "data/test_data/results"
    model_name = "seamless_audio_trainscriber"
    model_result_dir = os.path.join(result_dir, model_name)

    audio_to_exlude = ["audio_3.mp3"]

    audio_names = [audio_name for audio_name in os.listdir(audio_dir) if audio_name not in audio_to_exlude]
    audio_paths = [os.path.join(audio_dir, audio_name) for audio_name in audio_names]

    audio_transcriber: SeamlessAudioTranscriber = SeamlessAudioTranscriber(device=device)

    for audio_id, audio_path in enumerate(audio_paths):
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        print(f"{audio_id + 1}. {audio_name}")

        t1 = time.time()
        trancribe_result: AudioTranscriber.TranscribeResult = audio_transcriber.transcript_audio(audio_path)
        t2 = time.time()

        test_result_path = os.path.join(model_result_dir, audio_name)
        os.makedirs(test_result_path, exist_ok=True)
        

        audio = AudioSegment.from_file(audio_path)
        metadata = {
            "audio_duration": len(audio) / 1000,
            "transcription_time": t2 - t1,
            "duration_to_transcription_time_ratio": (t2 - t1) / (len(audio) / 1000),
            "num_segments": len(trancribe_result.segments),
            "num_speakers": len(set([segment.speaker_id for segment in trancribe_result.segments])),
            "segments": trancribe_result.__dict__()
        }

        metadata_path = os.path.join(test_result_path, 'meta.json')
        transcription_path = os.path.join(test_result_path, 'transcription.txt')

        with open(metadata_path, "w", encoding='utf-8') as file:
            json.dump(metadata, file, indent=2, ensure_ascii=False)
        
        with open(transcription_path, "w", encoding='utf-8') as file:
            file.write(str(trancribe_result))
