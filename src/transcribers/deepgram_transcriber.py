from typing import List
from src.transcribers.transcriber_interface import TranscriberInterface
from deepgram import DeepgramClient, PrerecordedOptions

class DeepgramTranscriber(TranscriberInterface):
    deepgram: DeepgramClient

    def __init__(self, api_key: str):
        self.deepgram = DeepgramClient(api_key)
    
    def transcript_audio(self, file_path: str) -> TranscriberInterface.TranscribeResult:
        with open(file_path, 'rb') as buffer_data:
            payload = { 'buffer': buffer_data }

            options = PrerecordedOptions(
                punctuate=True, model="nova-2", language="ru", diarize=True
            )

            response = self.deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)

        segments: List[TranscriberInterface.SpeakerData] = []
        text = ""
        speaker_id = -1
        words = response.results.channels[0].alternatives[0].words
        words += words[-1:] 
        for word_id, word in enumerate(words):
            if word.speaker != speaker_id or word_id == len(words) - 1:
                if speaker_id >= 0:
                    segments.append(TranscriberInterface.SpeakerData(speaker_id, text.strip(" ")))
                speaker_id = word.speaker
                text = ""
            text += word.punctuated_word + " "
        
        transcribe_result: TranscriberInterface.TranscribeResult = TranscriberInterface.TranscribeResult(segments)
        return transcribe_result