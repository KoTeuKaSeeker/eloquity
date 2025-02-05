import os
from pydub import AudioSegment
from src.file_extractors.file_extractor_interface import FileExtractorInterface

class AudioExtractor(FileExtractorInterface):
    def __init__(self):
        pass

    def extract_file(self, file_path: str, extracted_file_path: str, remove_parent: bool = True):
        extention = os.path.splitext(extracted_file_path)[1]

        audio_segment = AudioSegment.from_file(file_path)
        audio_segment.export(extracted_file_path, format=extention.lstrip("."))

        if remove_parent:
            os.remove(file_path)
        
        return extracted_file_path