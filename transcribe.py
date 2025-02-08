from src.transcribers.audio_transcriber import AudioTranscriber
from src.transcribers.sieve_audio_transcriber import SieveAudioTranscriber


if __name__ == "__main__":
    audio_path = "tmp/AwACAgIAAxkBAAIBg2ejJemwAwF-kGwJHokWoHwE68IlAAIecgACzt0ZSSYYNqupYWw0NgQ.wav"
    audio_transcriber: SieveAudioTranscriber = SieveAudioTranscriber()
    
    trancribe_result: AudioTranscriber.TranscribeResult = audio_transcriber.transcript_audio(audio_path)

    print(trancribe_result)