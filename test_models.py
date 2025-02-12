from src.transcribers.audio_transcriber import AudioTranscriber
from src.transcribers.sieve_audio_transcriber import SieveAudioTranscriber
from src.transcribers.antony_whisper_trainscriber import AntonyWhisperTranscriber
from src.transcribers.facebook_wisper_transcriber import FacebookWisperTranscriber
from src.transcribers.seamless_audio_transcriber import SeamlessAudioTranscriber
from src.transcribers.deepgram_transcriber import DeepgramTranscriber
import os
import time
import json
from pydub import AudioSegment
import torch
from src.eloquity_ai import EloquityAI
from src.transcribers.transcriber_interface import TranscriberInterface
import uuid


def extract_tasks_from_audio_file(docx_template_path: str, audio_path: str, model: EloquityAI, trancribe_result: TranscriberInterface.TranscribeResult):
    conversation = "\n".join(f"speaker_{segment.speaker_id}: {segment.text}" for segment in trancribe_result.segments)
    doc = eloquity.generate_docx(conversation, docx_template_path)

    return doc


def save_doc(self, doc) -> str:
    doc_path = os.path.join(self.temp_dir, str(uuid.uuid4()) + ".docx") 
    doc.save(doc_path)
    return doc_path


if __name__ == "__main__":
    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda'
    elif torch.backends.mps.is_available():
        device = 'mps'
        setattr(torch.distributed, "is_initialized", lambda : False) # monkey patching
    device = torch.device(device)

    gptunnel_api_key = "shds-748HxUWzKXVwSToCnkVp3opLXFC"

    audio_dir = "data/test_data/audio"
    result_dir = "data/test_data/llm-test-results"
    # ['gpt-4o', 'deepseek-3', 'deepseek-r1', 'qwen-2.5-72b-instruct', 'llama-3.1-405b']
    model_names = ['gpt-4o', 'deepseek-3', 'qwen-2.5-72b-instruct', 'llama-3.1-405b']
    docx_template_path = "docx_templates/default.docx"

    audio_to_exlude = ["audio_3.mp3"]

    audio_names = [audio_name for audio_name in os.listdir(audio_dir) if audio_name not in audio_to_exlude]
    audio_paths = [os.path.join(audio_dir, audio_name) for audio_name in audio_names]

    audio_transcriber: DeepgramTranscriber = DeepgramTranscriber("")


    for model_name in model_names:
        eloquity = EloquityAI(api_key=gptunnel_api_key, model_name=model_name)
        model_result_dir = os.path.join(result_dir, model_name)
        
        for audio_id, audio_path in enumerate(audio_paths):
            audio_path = os.path.normpath(audio_path)
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            print(f"{audio_id + 1}. {audio_name}")

            t1 = time.time()
            trancribe_result: AudioTranscriber.TranscribeResult = audio_transcriber.transcript_audio(audio_path)
            t2 = time.time()

            test_result_path = os.path.join(model_result_dir, audio_name)
            os.makedirs(test_result_path, exist_ok=True)
            
            audio = AudioSegment.from_file(audio_path)
            metadata = {
                "transcription_time": t2 - t1,
                "audio_duration": len(audio) / 1000,
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
            
            doc = extract_tasks_from_audio_file(docx_template_path, audio_path, eloquity, trancribe_result)
            doc.save(os.path.join(test_result_path, f"{model_name}.docx"))