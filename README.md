# Eloquity

![alt text](assets/img1.jpg)

## Описание

**Eloquity** - это пакет для генерации документов на основе текстовых данных. Пакет позволяет создавать документы в формате docx на основе текстовых данных, а также определять исполнителей задач на основе текстовых данных.

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

## Быстрый старт
Ниже приведён минимальный пример кода того, как можно использовать библиотеку.
Данный пример выполняет следующие шаги:

1. Загрузка файл беседы
2. Создание экземпляр модели `EloquityAI` с API-ключом
3. Генерация документа (docx) на основе переданного текста беседы
4. Сохранение созданного документа

Минимальный пример кода:
```py
from src.eloquity_ai import EloquityAI

# Загрузка файл беседы
with open("examples/data/conv_0.txt", "r", encoding="utf-8") as file:
    conversation = file.read()

# Создание экземпляр модели EloquityAI с API-ключом
model = EloquityAI(api_key="YOUR_API_KEY")

# Генерация документа (docx) на основе переданного текста беседы
doc = model.generate_docx(conversation)

# Сохранение созданного документа
doc.save('tasks.docx')
```

## Формат входных данных
Методы класс `EloquityAI` принимают строку с беседой. Беседа имеет следующий формат:

```sh
speaker_0: text_0
speaker_1: text_1
speaker_0: text_0
```

Здесь `speaker_n` означает заданное имя говорящего, а соответвущий ему `text_0` - то, что этот человек сказал.

Примеры входных строк можно найти в папке `examples/data`

## Запуск Telegram бота
**Eloquity** имеет телеграм бота которого можно запустить локально из этого репозитория. Для этого нужно следовать шагам, описанным ниже.
### 1. Подготовка .env файла
Сначала нжно создать файл а дать ему название `.env `. Затем его нужно заполнить следующим образом:
```py
API_KEY="YOUR_KEY"
```

1. `API_KEY` - API ключ от акканту на сервисе [GPTunnel](https://gptunnel.ru/)

### 2. Запуск бота
Чтобы запустить бота, нужно запустить скрипт `bot.py`:
```sh
python bot.py
```