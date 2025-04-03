from abc import ABC, abstractmethod

class DocumentGeneratorInterface(ABC):
    @abstractmethod
    def generate_document(self, document_data: dict, save_path: str):
        pass