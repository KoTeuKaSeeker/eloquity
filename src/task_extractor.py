import os
import uuid
from src.eloquity_ai import EloquityAI
from src.transcribers.transcriber_interface import TranscriberInterface


class TaskExtractor():
    audio_transcriber: TranscriberInterface
    eloquity: EloquityAI
    docx_template_path: str
    temp_dir: str

    def __init__(self, audio_transcriber: TranscriberInterface, eloquity: EloquityAI, docx_template_path: str, temp_dir: str = "tmp/"):
        self.audio_transcriber = audio_transcriber
        self.eloquity = eloquity
        self.docx_template_path =docx_template_path
        self.temp_dir = temp_dir

        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_tasks_from_audio_file(self, audio_path: str, json_log: dict = None):
        trancribe_result: TranscriberInterface.TranscribeResult = self.audio_transcriber.transcript_audio(audio_path)

        if json_log is not None:
            json_log["transcribe_result"] = trancribe_result.__dict__()

        conversation = "\n".join(f"speaker_{segment.speaker_id}: {segment.text}" for segment in trancribe_result.segments)
        doc = self.eloquity.generate_docx(conversation, self.docx_template_path, json_log=json_log)

        return doc
    
    def save_doc(self, doc, save_path: str = None) -> str:
        doc_path = os.path.join(self.temp_dir, str(uuid.uuid4()) + ".docx") if save_path is None else save_path
        doc.save(doc_path)
        return doc_path
    
    def extract_and_save_tasks(self, audio_path: str, save_path: str = None, json_log: dict = None):
        doc = self.extract_tasks_from_audio_file(audio_path, json_log)
        doc_path = self.save_doc(doc, save_path=save_path)
        return doc_path
