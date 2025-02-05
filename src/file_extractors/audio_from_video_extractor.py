import os
from pydub import AudioSegment
from src.file_extractors.file_extractor_interface import FileExtractorInterface
from src.exeptions.unknown_error_exception import UnknownErrorException
from moviepy import VideoFileClip

class AudioFromVideoExtractor(FileExtractorInterface):
    def __init__(self):
        pass

    def extract_file(self, file_path: str, extracted_file_path: str, remove_parent: bool = True):
        try:
            video = VideoFileClip(file_path)
            video.audio.write_audiofile(extracted_file_path, codec="pcm_s16le")
            video.close()

            if remove_parent:
                os.remove(file_path)

            return extracted_file_path
        except Exception as e:
            raise UnknownErrorException()