from typing import Dict, List
from src.commands.transcibe_llm_command import TranscibeLLMCommand
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.chat.chat_interface import ChatInterface
from src.docs.document_generator_interface import DocumentGeneratorInterface
from src.drop_box_manager import DropBoxManager
import traceback
import re
import yaml
import os
import json
import uuid

class HrLLMCommand(TranscibeLLMCommand):
    default_report_formats: Dict[str, str]
    report_document_generator: DocumentGeneratorInterface
    report_generation_model: LLMInterface
    table_generation_model: LLMInterface

    def __init__(self, chatting_model: LLMInterface, report_generation_model: LLMInterface, table_generation_model: LLMInterface, filter_factory: MessageFilterFactoryInterface, transcriber: TranscriberInterface, report_document_generator: DocumentGeneratorInterface, temp_path: str, entry_point_state: str, formats_folder_path: str, dropbox_manager: DropBoxManager):
        super().__init__(chatting_model, filter_factory, transcriber, temp_path, entry_point_state, dropbox_manager)
        self.report_document_generator = report_document_generator
        self.report_generation_model = report_generation_model
        self.table_generation_model = table_generation_model
        self.chatting_state = "hr_llm_command.chatting_state"
        self.waiting_format_state = "hr_llm_command.waiting_format_state"
        self.waiting_format_name_state = "hr_llm_command.waiting_format_name_state"
        self.waiting_format_text_state = "hr_llm_command.waiting_format_text_state"
        self.waiting_remove_format_state = "hr_llm_command.waiting_remove_format_state"
        self.default_report_formats = self.load_default_formats(formats_folder_path)
        self.system_prompt =  """
Ты — помощник по анализу транскрипций интервью. Тебя зовут Production HR Manatee. Твоя задача — на основе предоставленной транскрибации интервью составить отчет-оценку кандидата, следуя указанному пользователем формату. Ты должен точно и структурированно следовать тому, как пользователь запросил вывод.

Интерфейс:
1. Входной запрос будет содержать текст транскрипции интервью после фразы "Транскрипция интервью:".
2. Пользователь также предоставит формат отчета, который ты должен строго придерживаться.
3. Ты должен анализировать транскрипцию интервью и заполнять отчет в соответствии с предоставленным пользователем форматом.
                                     
ВАЖНО:
1. Напомню ещё раз - твоя главная задача помогать HR специалистам отбирать кандидатов. Ты анализируешь интервью и по нему делаешь отчёт-оценку кандидата, чтобы HR-у было проще отобрать специалиста.
2. Если пользователь не предоставил формат, тогда ты ДОЛЖЕН вывести отчет с включением следующих разделов: "Технические навыки", "Софт скилы", "Хард скилы", "Соответствие запросу", "Вывод"
3. Если пользователь ввёл что то, не связанное с интервью и форматом, ты ДОЛЖЕН попросить его предоставить информацию и том, на какую должность было проведено интервью и также сказать что пользователь может при желании указать формат.
4. Не говори с пользователем на какие либо отвлечённые задачи, у тебя едиственная задача - предоставить отчет по интервью.
5. Если тебе точно не предоставили формат, который нужно использовать, тебе не нужно его расписывать пользователю. Сразу пиши отчёт, а формат придумывай на ходу.
6. Твоя задача делать отчёт не оп чек листу, не по плану чек листа, не по шаблону отчёта, а именно отчёт по интервью. НЕ ДЕЛАЙ НИКАКИЕ ДРУГИЕ ОТЧЁТЫ!!!
7. НИКАКИЕ ПРЕДВАРИТЕЛЬНЫЕ ПЛАНЫ ПИСАТЬ НЕ НУЖНО!!! Сразу пиши отчёт и всё, пожалуйсто

Порядок действий:
1. Попроси пользователя предоставить формат отчёта и чек лист.
2. Используй предоставленную информацию составь отчёт по интервью (ВАЖНО: не по чек листу, а по интервью. Твоя задача проанализировать интервью)
3. Продолжай обсуждение интервью с пользователем.
"""

    def load_default_formats(self, formats_folder_path):
        report_formats = {}
        for format_filename in os.listdir(formats_folder_path):
            format_file_path = os.path.join(formats_folder_path, format_filename)
            
            with open(format_file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            
            report_formats[data["format_name"]] = data["format_text"]
        
        return report_formats
    
    def get_report_formats(self, context: dict) -> dict:
        if "report_formats" not in context["user_data"]:
            context["user_data"]["report_formats"] = {}
            context["user_data"]["report_formats"].update(self.default_report_formats)
        
        return context["user_data"]["report_formats"]

    async def select_format_message(self, message: dict, context: dict, chat: ChatInterface):
        report_formats = self.get_report_formats(context)

        format_names = report_formats.keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(format_names)])
        if len(format_list) == 0:
            format_list = "(список форматов пуст)"

        keyboard = [["Добавить новый формат", "Удалить существующий формат"]]
        keyboard_keys = [["a", "b"]]
        await chat.send_keyboad(f"⏮️ Теперь выберите номер формата, в соответствии с которым вы хотите получить отчёт:\n{format_list}", keyboard, keyboard_keys)

        return chat.move_next(context, self.waiting_format_state)

    async def after_transcribe_message(self, message: dict, context: dict, chat: ChatInterface):
        return await self.select_format_message(message, context, chat)
    
    def get_discrimination_message(self, messages_for_discrimination: List[dict]) -> str:
        messages_history = messages_for_discrimination.copy()
        for message in messages_history:
            message["role"] = "user"

        discrimination_prompt = """
            Попробуй в сгенерированном тексте таблицы найти как можно больше несоответствий и ошибок в формате (почти точно они есть). Подробно распиши их и расскажи, 
            как генерировать таблицу, чтобы было всё правильно. Твои замечания затем будут отправляться другой модели, которая будет на основе них пытаться сделать как можно более
            корректную таблицу. Ты выступаешь в роли дискриминатора.

            Если же таблица сгенерированна полность корректно, в ответ просто ничего не пиши.

            P. S. Не забуть в конце попросить другую модель, которой будет посылаться твой ответ сгенерировать таблицу в json формате.
        """

        discrimination_message = {"role": "user", "content": discrimination_prompt}
        messages_history.append(discrimination_message)
        discrimation_respose = self.table_generation_model.get_response(messages_history)
        
        return discrimation_respose


    def generate_document_with_correction(self, document_path: str, messages_for_table_generation: List[dict], count_correction: int = 5) -> dict:
        messages_history = messages_for_table_generation.copy()

        count_tries = 0
        while count_tries < count_correction:
            excel_response = self.table_generation_model.get_response(messages_history)
            messages_history.append(excel_response)
            
            try:
                table_data = json.loads(excel_response["content"])
                self.report_document_generator.generate_document(table_data, document_path)

                discrimination_messages = [messages_history[0], messages_history[1], excel_response]
                discrimination_message = self.get_discrimination_message(discrimination_messages)
                discrimination_message["role"] = "user"

                if len(discrimination_message["content"]) == 0:
                    table_data = json.loads(excel_response["content"])
                    self.report_document_generator.generate_document(table_data, document_path)
                    return document_path

                messages_history.append(discrimination_message)
            except Exception as e:
                traceback_str = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))

                correction_prompt = f"""
                    Ты сгенерировал таблицу некорректно, поэтому при попытки преобразования ещё в json или создания из неё excel документа произошла ошибка. Вот как выгялдит текст ошибки:
                    {traceback_str}

                    Повтори генерацию таблицы, но на этот раз сделай так, чтобы она была корректной.
                """
                correction_message = {"role": "user", "content": correction_prompt}
                messages_history.append(correction_message)
        
        raise ValueError(f"Не удалось распарсить ответ модели для генерации таблицы.")


    async def generate_report(self, message: dict, context: dict, chat: ChatInterface):
        if "messages_history" not in context["chat_data"]:
            context["chat_data"]["messages_history"] = [{"role": "system", "content": self.system_prompt}]
        
        format_name = context["chat_data"]["format_name"]
        report_format = context["chat_data"]["report_format"]
        
        messages_history: list = context["chat_data"]["messages_history"]
        transcription_message = messages_history[-1]

        format_prompt = f"""
        Также вместе с транскрипцией известно о том, в каком именно формате необходимо составлять отчёт. Формат называется '{format_name}' и выглядит следующим образом:
        {report_format}

        ОЧЕНЬ ВАЖНО:
        Прошу тебя оформать отчёт не в md формате, как ты обычно делаешь, а в обычном текстовом формате с использование смайликов для более красивого оформления. Смотри, что я имею ввиду.
        Во-перых, ты не можешь использовать **текст** для того, чтобы сделать его жирным. Ты не можешь создавать таблицы с помощью md формата - чтобы сделать табличку, лучше
        используй обычное перечисление по пунктам. Например, вот так:
        1. 👋 Софт скилы:
            • Коммуникативность - 2.3
            • Командная работа - 3.5
            • Лидерство - 1.0
        2. 🖥️ Технические навыки:
            • Python - 4.5
            • Java - 3.0
            • C++ - 2.0
        
        Ещё раз тебе повторю - НЕ ДЕЛАЙ НИКАКОЙ ТЕКСТ ЖИРНЫМ (с помощью **), НЕ ДЕЛАЙ ЗАГОЛОВКИ (с помощью #). Форматировани md не работает там, где я буду использовать
        твой ответ.
        """

        format_message = {"role": "user", "content": format_prompt}
        messages_for_report = [transcription_message, format_message]

        model_response = self.report_generation_model.get_response(messages_for_report)
        messages_history.append(model_response)

        excel_prompt = """
            Теперь необходимо сгенерировать этот же формат, только не текстом, а в json формате, который будет описывать таблицу следующим образом:
            {
                "columns": {
                    "column_dict_0": {
                        "width": 30,
                        "column": [
                            {"0": "cell_name_10", "border": true, "bold": true},
                            {"1": "cell_name_11", "border": false, "bold": true},
                            ...
                            {"m": "cell_name_1m", "border": false, "bold": true},
                        ]
                    },
                    "column_dict_1": {
                        "width": 15,
                        "column": [
                            {"0": "cell_name_20", "border": false, "bold": false},
                            {"1": "cell_name_21", "border": true, "bold": true},
                            ...
                            {"m": "cell_name_2m", "border": true, "bold": true},
                        ]
                    }
                    ...
                    "column_dict_n": {
                        "width": 40,
                        "column": [
                            {"0": "cell_name_n0", "border": true, "bold": true},
                            {"1": "cell_name_n1", "border": true, "bold": false},
                            ...
                            {"m": "cell_name_nm", "border": false, "bold": false},
                        ]
                    }
                }

                "row_data": {
                    "0": {
                        "height": 20
                    },
                    "2": {
                        "height": 30
                    },
                    "10": {
                        "height": 15
                    }
                }
            }

            Здесь названия колонок ты так и должен оставлять как column_dict_i, где i - номер колонки, а вот названия клеток заменять на то, 
            что ты хочешь поместить в соотвествующую клетку таблицы. Также, как ты можешь заметить, у колонки есть такой параметр как width - с помощью
            него ты можешь настраивать ширину колонки, чтобы большой текст мог поместиться в ячейках. Используй это, чтобы табличка выглядела красиво (хочу заметить, что в табличке используется перенос строк, 
            поэтому тебе не обязательно расширять колонку так, чтобы всё влезло в виде одной строки. Даже красивее будет, если всё будет помещаться в виде нескольких строк. Вообщем, находи баланс).

            Теперь по поводу того, как располагать данные. В первой колонке таблици должны находиться как бы заголовки. Сначала идёт заголовок топика, например "общая информация", а далее несколько заголовков, 
            которые входят в этот топик, например "ФИО", "Дата собеседования", "Должность" и т.д. После того, как заголовки топика закончились, идут две пустые клетки, обозначающие конец топика и дальше заголовок нового топика, например "Технические навыки", далее опять
            заголовки, которые входят в этот топик и опять две клетки пропущено и так повторяется до конца, пока все заголовки не будут расписаны. ВНИМАНИЕ: !!!Все заголовки должны быть выделены жирным шрифтом (параметр "bold": true у ячейки)!!!

            Во второй колонке таблицы должны находиться значения, которые соответствуют заголовкам. Например, напротив заголовка "ФИО" должна находиться строчка с ФИО, напротив заголовка "Должность" должна располагаться должность кандидата и т.д. Ячейки во второй колонке,
            которые находятся напротив заголовков-топиков (ещё раз напомню, что заголовки-топики - это заголовки, такие как "Общая информация", "Резюме и опыт", "Технические навыки" и т.д) должны содержать слово "Значение" и эта ячейка также должна иметь жирный шрифт.

            Теперь по поводу границ/обводки. Границы должны быть включены у всех ячеек, в которых находятся заголовки (кроме пустых ячеек, разделяющих заголовки-топики) и во всех ячейках, в которых находятся значения заголовков (вторая колонка) - опять же, кроме тех пустых ячеек, которые 
            разделяют заголовки-топики.

            Также смотри, ниже самого словаря с табличкой, должен быть словарь "row_data", который описывает ширину некоторых из строк (можешь заметить, что совсем не обязательно всех. Если не указывать высоту строки, то она будет ставиться автоматически).

            ВАЖНО:
            1. Твоё ответ должен содержать чисто текст с json форматом, без каких-либо оборачивающих кавычек.
            2. В ответе нельзя писать ничего кроме json формата, иначе программе не удасться его распарсить и вылетит ошибка (а это очень и очень плохо).
        """
        excel_message = {"role": "user", "content": excel_prompt}
        messages_for_table_generation = [transcription_message, format_message, model_response, excel_message]

        excel_response = self.table_generation_model.get_response(messages_for_table_generation)
        table_data = json.loads(excel_response["content"])

        document_name = str(uuid.uuid4())
        document_path = os.path.join(self.temp_path, document_name + ".xlsx")
        self.report_document_generator.generate_document(table_data, document_path)

        await chat.send_message_to_query(model_response["content"])
        await chat.send_file_to_query(document_path)

        keyboard = [["Создать dropbox ссылку"]]
        keyboard_keys = [["/create_dbx"]]
        await chat.send_keyboad("⏮️ Сейчас можете продолжить беседу с ботом - он имеет транскрибацию и отчёт в памяти.", keyboard, keyboard_keys)

        return chat.move_next(context, self.chatting_state)

    async def select_report_format(self, message: dict, context: dict, chat: ChatInterface):
        report_formats = self.get_report_formats(context)

        format_id = int(re.findall(r"\d+", message["text"])[0]) - 1
        format_names = list(report_formats.keys())

        if format_id < 0 or format_id >= len(format_names):
            return await self.wrong_select_format_messsage(message, context, chat)
        
        format_name = format_names[format_id]
        report_format = report_formats[format_name]

        context["chat_data"]["format_name"] = format_name
        context["chat_data"]["report_format"] = report_format

        await chat.remove_keyboad(f'✒️ Вы выбрали формат "{format_name}". Сейчас в сооветствии с ним будет составлен отчёт о кандидате 😉')
        
        return await self.generate_report(message, context, chat)


    async def response_format_name_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.remove_keyboad("✒️ Напишите название формата, который вы хотите добавить.")
        return chat.move_next(context, self.waiting_format_name_state)
    
    async def response_format_text_command(self, message: dict, context: dict, chat: ChatInterface):
        context["chat_data"]["format_name"] = message["text"]
        await chat.send_message_to_query("📌 Теперь отправьте текст, который описывал бы формат. Этот текст будет посылаться напрямую в языковую модель, так что описание формата может быть произвольным - главное объяснить его доходчиво 🚀.")
        return chat.move_next(context, self.waiting_format_text_state)

    async def add_format_command(self, message: dict, context: dict, chat: ChatInterface):
        format_name = context["chat_data"]["format_name"]
        format_text = message["text"]

        report_formats = self.get_report_formats(context)
        
        report_formats[format_name] = format_text
        await chat.send_message_to_query("✅ Новый формат был успешно добавлен!")
        return await self.select_format_message(message, context, chat)
    
    async def wrong_format_text_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("💀 Вы некорректно ввели формат отчёта. Введите формат отчёта ещё раз.")
        return chat.stay_on_state(context)
    
    async def wrong_format_name_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Вы отправили некорректное название формата. Напишите название формата отчёта.")
        return chat.stay_on_state(context)

    async def wrong_select_format_messsage(self, message: dict, context: dict, chat: ChatInterface):
        format_names = self.get_report_formats(context).keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(format_names)])
        if len(format_list) == 0:
            format_list = "(список форматов пуст)"
        keyboard = [["Добавить новый формат", "Удалить существующий формат"]]
        keyboard_keys = [["a", "b"]]
        await chat.send_keyboad(f"🪡 Вы отправили некорректный номер формата. Выберите желаемый формат для составления отчёта из следующего списка:\n{format_list}", keyboard, keyboard_keys)
        return chat.move_next(context, self.waiting_format_state)

    async def response_remove_format_name_command(self, message: dict, context: dict, chat: ChatInterface):
        report_formats: dict = self.get_report_formats(context)
        removeable_report_format_keys = report_formats.keys() - self.default_report_formats.keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(removeable_report_format_keys)])
        if len(removeable_report_format_keys) == 0:
            format_list = "(нет форматов, которые можно удалить)"
        
        keyboard = [["Отменить"]]
        keyboard_keys = [["a"]]
        await chat.send_keyboad(f"💀 Введите номер формата, который вы хотите удалить:\n{format_list}\n\n🔎 Можете заметить, что здесь список форматов неполный, так как стандартные форматы удалить нельзя.", keyboard, keyboard_keys)
        return chat.move_next(context, self.waiting_remove_format_state)
    
    async def wrong_select_format_to_remove_messsage(self, message: dict, context: dict, chat: ChatInterface):
        report_formats: dict = self.get_report_formats(context)
        removeable_report_format_keys = report_formats.keys() - self.default_report_formats.keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(removeable_report_format_keys)])
        if len(removeable_report_format_keys) == 0:
            format_list = "(нет форматов, которые можно удалить)"
        keyboard = [["Отменить"]]
        keyboard_keys = [["a"]]
        await chat.send_keyboad(f"⚙️ Вы отправили некорректный номер формата. Введите номер формата, который вы хотите удалить:\n{format_list}", keyboard, keyboard_keys)
        return chat.stay_on_state(context)
    
    async def select_report_format_to_remove(self, message: dict, context: dict, chat: ChatInterface):
        report_formats: dict = self.get_report_formats(context)
        removeable_report_format_keys = report_formats.keys() - self.default_report_formats.keys()

        format_id = int(re.findall(r"\d+", message["text"])[0]) - 1
        format_names = list(removeable_report_format_keys)

        if format_id < 0 or format_id >= len(format_names):
            return await self.wrong_select_format_to_remove_messsage(message, context, chat)
        
        format_name = format_names[format_id]
        del report_formats[format_name]

        await chat.send_message_to_query(f'Формат "{format_name}" был успешно удалён ✅')
        return await self.select_format_message(message, context, chat)
    
    async def cancel_remove_format_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.remove_keyboad(f'🔖 Удаление формата отменено.')
        return await self.select_format_message(message, context, chat)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        states = super().get_conversation_states()
        states.update({
            self.waiting_format_state: [
                MessageHandler(self.filter_factory.create_filter("equal", dict(messages=["Добавить новый формат", "a", "а"])), self.response_format_name_command),
                MessageHandler(self.filter_factory.create_filter("equal", dict(messages=["Удалить существующий формат", "b"])), self.response_remove_format_name_command),
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"\d+")), self.select_report_format),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_select_format_messsage)
            ],
            self.waiting_format_name_state: [
                MessageHandler(self.filter_factory.create_filter("text"), self.response_format_text_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_format_name_message)
            ],
            self.waiting_format_text_state: [
                MessageHandler(self.filter_factory.create_filter("text"), self.add_format_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_format_text_message)
            ],
            self.waiting_remove_format_state: [
                MessageHandler(self.filter_factory.create_filter("equal", dict(messages=["Отменить", "a", "а"])), self.cancel_remove_format_command),
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"\d+")), self.select_report_format_to_remove),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_select_format_to_remove_messsage)
            ]
        })

        return states