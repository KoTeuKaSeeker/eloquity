from abc import ABC, abstractmethod

class FileExtractorInterface(ABC):
    @abstractmethod
    def extract_file(self, file_path: str, extracted_file_path: str, remove_parent: bool = True) -> str:
        pass