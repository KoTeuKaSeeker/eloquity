import os
from dotenv import load_dotenv
from src.task_extractor import TaskExtractor
from src.transcribers.deepgram_transcriber import DeepgramTranscriber
from src.eloquity_ai import EloquityAI

# Загрузка переменных окружения
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY") # Ключ к API сервиса транскрибации https://deepgram.com/
GPTUNNEL_API_KEY = os.getenv("GPTUNNEL_API_KEY") # Ключ к API сервиса с языковами моделями https://gptunnel.ru/
DOCX_TEMPLATE_PATH = "docx_templates/default.docx" # Файл .docx со стилями форматирования 
TEMP_DIR = "tmp/" # Путь для хранения промежуточных файлов

audio_path = "examples/data/audio_1.wav" # Путь до аудиозаписи беседы

if __name__ == "__main__":
    # Инициализация транскрибатора на основе Deepgram (можно выбрать и другой транскрибатор, сейчас реализованно 6 различных вариантов, см. "src/transcribers/")
    transcriber = DeepgramTranscriber(DEEPGRAM_API_KEY)

    # Инициализация языковой модели GPT4o на основе API GPTunnel
    eloquity = EloquityAI(GPTUNNEL_API_KEY)

    # Инициализация экстрактора задач
    task_extractor = TaskExtractor(transcriber, eloquity, DOCX_TEMPLATE_PATH, TEMP_DIR)

    # Извлечение задач из аудиозаписи в формате docx
    doc = task_extractor.extract_tasks_from_audio_file(audio_path)
    
    # Сохранение извлечённых задач в документ
    doc.save("tasks.docx")