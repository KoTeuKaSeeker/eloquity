from typing import List

class NotSupportedFormatException(ValueError):
    not_supported_format: str
    audio_formats: List[str]
    video_formats: List[str]

    def __init__(self, not_supported_format: str, audio_formats: List[str], video_formats: List[str]):
        self.not_supported_format = not_supported_format
        self.audio_formats = audio_formats
        self.video_formats = video_formats

        general_message = f'Формат "{self.not_supported_format}" не поддерживается. На данный момент поддерживаются следующие форматы:'
        audio_formats = 'Для аудио: ' + ", ".join(self.audio_formats)
        video_formats =  'Для видео: ' + ", ".join(self.video_formats)

        message = f'{general_message}\n    🔉 {audio_formats}\n    📽️ {video_formats}\n'

        super().__init__(message, not_supported_format, audio_formats, video_formats)