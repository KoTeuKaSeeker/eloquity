from typing import Dict
from src.commands.transcibe_llm_command import TranscibeLLMCommand
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.chat.chat_interface import ChatInterface
import re
import yaml
import os

class HrLLMCommand(TranscibeLLMCommand):
    default_report_formats: Dict[str, str]

    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface, transcriber: TranscriberInterface, temp_path: str, entry_point_state: str, formats_folder_path: str):
        super().__init__(model, filter_factory, transcriber, temp_path, entry_point_state)
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

        await chat.send_message_to_query(f"⏮️ Теперь выберите номер формата, в соответствии с которым вы хотите получить отчёт:\n{format_list}\n\n 🔖 Если же вы хотите добавить новый формат отчёта, выполните команду /add_format. Если вы хотите удалить существующий формат, выплоните команду /remove_format")

        return chat.move_next(context, self.waiting_format_state)

    async def after_transcribe_message(self, message: dict, context: dict, chat: ChatInterface):
        return await self.select_format_message(message, context, chat)

    async def select_report_format(self, message: dict, context: dict, chat: ChatInterface):
        report_formats = self.get_report_formats(context)

        format_id = int(re.findall(r"\d+", message["text"])[0]) - 1
        format_names = list(report_formats.keys())

        if format_id < 0 or format_id >= len(format_names):
            return await self.wrong_select_format_messsage(message, context, chat)
        
        format_name = format_names[format_id]
        report_format = report_formats[format_name]

        await chat.send_message_to_query(f'✒️ Вы выбрали формат "{format_name}". Сейчас в сооветствии с ним будет составлен отчёт о кандидате 😉')
        
        if "messages_history" not in context["chat_data"]:
            context["chat_data"]["messages_history"] = [{"role": "system", "content": self.system_prompt}]
        
        messages_history: list = context["chat_data"]["messages_history"]
        messages_history.append({"role": "user", "content": f"Также вместе с транскрипцией известно о том, в каком именно формате необходимо составлять отчёт. Формат называется '{format_name}' и выглядит следующим образом:\n{report_format}"})

        model_response = self.model.get_response(messages_history)
        messages_history.append(model_response)

        await chat.send_message_to_query(model_response["content"])
        await chat.send_message_to_query("⏮️ Сейчас можете продолжить беседу с ботом - он имеет транскрибацию и отчёт в памяти.")

        return chat.move_next(context, self.chatting_state)

    async def response_format_name_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("✒️ Напишите название формата, который вы хотите добавить.")
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
        await chat.send_message_to_query(f"🪡 Вы отправили некорректный номер формата. Выберите желаемый формат для составления отчёта из следующего списка:\n{format_list}")
        return chat.move_next(context, self.waiting_format_state)

    async def response_remove_format_name_command(self, message: dict, context: dict, chat: ChatInterface):
        report_formats: dict = self.get_report_formats(context)
        removeable_report_format_keys = report_formats.keys() - self.default_report_formats.keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(removeable_report_format_keys)])
        if len(removeable_report_format_keys) == 0:
            format_list = "(нет форматов, которые можно удалить)"
        
        await chat.send_message_to_query(f"💀 Введите номер формата, который вы хотите удалить:\n{format_list}\n\n🔎 Можете заметить, что здесь список форматов неполный, так как стандартные форматы удалить нельзя. Если вы хотите отменить удаление формата, выполните команду /cancel")
        return chat.move_next(context, self.waiting_remove_format_state)
    
    async def wrong_select_format_to_remove_messsage(self, message: dict, context: dict, chat: ChatInterface):
        report_formats: dict = self.get_report_formats(context)
        removeable_report_format_keys = report_formats.keys() - self.default_report_formats.keys()
        format_list = "\n".join([f"{i+1}. {format_name}" for i, format_name in enumerate(removeable_report_format_keys)])
        if len(removeable_report_format_keys) == 0:
            format_list = "(нет форматов, которые можно удалить)"
        await chat.send_message_to_query(f"⚙️ Вы отправили некорректный номер формата. Введите номер формата, который вы хотите удалить:\n{format_list}")
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
        await chat.send_message_to_query(f'🔖 Удаление формата отменено.')
        return await self.select_format_message(message, context, chat)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        states = super().get_conversation_states()
        states.update({
            self.waiting_format_state: [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="add_format")), self.response_format_name_command),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="remove_format")), self.response_remove_format_name_command),
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
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"\d+")), self.select_report_format_to_remove),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel_remove_format_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_select_format_to_remove_messsage)
            ]
        })

        return states