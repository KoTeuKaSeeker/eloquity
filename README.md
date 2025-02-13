# Eloquity

![alt text](assets/img1.jpg)

## Описание

**Eloquity** – это пакет для анализа бесед и генерации списка задач. Он позволяет обрабатывать текстовые данные и автоматически формировать документы в формате `DOCX` с перечнем задач и их исполнителей.

Пакет использует `ChatGPT-4o` для анализа диалогов и выделения ключевых задач, а также поддерживает интеграцию с `Telegram-ботом`, который дополнительно умеет транскрибировать аудио и видео перед обработкой.

## Требования
Подходящяя версия `Python`:
```sh
Python 3.11.9
```

### 1. Установка зависимостей
1\. Создание виртуального окружения `Python`:
```sh
python -m venv venv
```
2\. Активация окружения:
```sh
# Linux
source venv/bin/activate

# Windows
.\venv\Scripts\activate.bat
```

3\. Обновление пакетного менеджера `pip` до последней версии:
```sh
# Linux
pip install --upgrade pip

# Windows
python.exe -m pip install --upgrade pip
```

4\. Установка `Python` зависимосимостей:
```sh
pip install -r requirements.txt
```
### 2. Установка PyTorch
Команду для установки можно подобрать под свою систему с официального сайта [PyTorch](https://pytorch.org/get-started/locally/).

Пример для `CUDA 12.4` на `Windows`: 
```sh
# Установка PyTorch на GPU с CUDA 12.4
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## Запуск Telegram бота
**Eloquity** имеет телеграм бота которого можно запустить локально из этого репозитория. Для этого нужно следовать шагам, описанным ниже.
### 1. Подготовка .env файла
Сначала нужно создать файл и дать ему название `.env `. Затем его необходимо заполнить следующим образом:
```py
GPTUNNEL_API_KEY = "<specify_your_key>"
TELEGRAM_BOT_TOKEN = "<specify_your_token>"
HUGGING_FACE_TOKEN = "<specify_your_token>"
DROPBOX_APP_KEY = "<specify_your_key>"
DROPBOX_APP_SECRET = "<specify_your_secret>"
DROPBOX_REFRESH_TOKEN = "<specify_your_refresh_token>"
DEEPGRAM_API_KEY = "<specify_your_key>"
```

1. `GPTUNNEL_API_KEY` - API-ключ для сервиса [GPTunnel](https://gptunnel.ru/)
2. `TELEGRAM_BOT_TOKEN` - Токен [телегам](https://web.telegram.org/) бота
3. `HUGGING_FACE_TOKEN` - Токен от [huggingface](https://huggingface.co/)
4. `DROPBOX_APP_KEY` - Ключ приложения в [dropbox](https://www.dropbox.com/). Подробнее от том, как создать своё приложение в dropbox можно найти в следующем [видео](https://www.youtube.com/watch?v=cj7A-CjL-wI)
5. `DROPBOX_APP_SECRET` - Секретный ключ приложения в [dropbox](https://www.dropbox.com/). Информацию о нём можно найти также, как и в пункте выше, в следующем [видео](https://www.youtube.com/watch?v=cj7A-CjL-wI) 
6. `DROPBOX_REFRESH_TOKEN` - Возобнавляемый токен от приложения [dropbox](https://www.dropbox.com/). Его получить относительно "муторно", но подробнее о том, как это делается можно найте в следующем [видео](https://www.youtube.com/watch?v=y0tBLoSfjxc)
7. `DEEPGRAM_API_KEY` - API-ключ от сервиса [deepgram](https://deepgram.com/)

### 2. Запуск бота
Чтобы запустить бота, нужно запустить скрипт `bot.py`:
```sh
python bot.py
```

## Быстрый старт
Ниже приведён минимальный пример кода того, как можно использовать библиотеку.
Данный пример выполняет следующие шаги:

1. Создание экземпляра транскрибатора `DeepgramTranscriber` с API-ключом
2. Создание экземпляр модели `EloquityAI` с API-ключом
3. Генерация извлечённых задач в формате docx на основе переданного пути до аудиозаписи беседы
4. Сохранение документа по пути "tasks.docx"

Минимальный пример кода:
```py
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
```