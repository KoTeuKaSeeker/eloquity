import requests
import re
from datetime import datetime, timedelta
from typing import List
import yaml
from docx import Document
from docx.shared import Pt


class Task:
    def __init__(self, content: str, deadline: datetime):
        self.content = content
        self.deadline = deadline
    
    def __str__(self):
        return f"({self.deadline}) {self.content}"


class Assignee:
    def __init__(self, name: str, tasks: List[Task]):
        self.name = name
        self.tasks = tasks
    
    def __str__(self):
        output = f"{self.name}:\n"
        for task in self.tasks:
            output += f"\t{task}\n"
        return output


class EloquityAI:
    def __init__(self, api_key: str):
        self.api_url = "https://gptunnel.ru/v1/chat/completions"
        self.api_key = api_key
        self.name_identification_prefix = self._load_prefix("prefixes/name_identification.txt")
        self.task_assigment_prefix = self._load_prefix("prefixes/task_assigment.txt")

    def _load_prefix(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return ""

    def get_model_response(self, message):
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": message}]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        content = response.json()["choices"][0]["message"]["content"]

        return content
    
    def get_delta_time_from_str(self, time_string):
        pattern = r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
        
        matches = re.match(pattern, time_string)
        
        if matches:
            days = int(matches.group(1) or 0)
            hours = int(matches.group(2) or 0)
            minutes = int(matches.group(3) or 0)
            seconds = int(matches.group(4) or 0)
            
            return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        
        return timedelta()
    
    
    def generate_assignees(self, conversation_str: str) -> List[Assignee]:
        name_dict = self.identify_assignee_names(conversation_str)

        def replace_speakers(text, speakers):
            pattern = re.compile(r'\b(speaker_\d+)\b')  # Match words like speaker_0
            return pattern.sub(lambda match: f"[{speakers.get(match.group(1), match.group(1))}]", text)
        
        conversation_str = replace_speakers(conversation_str, name_dict)
        
        content = self.task_assigment_prefix + conversation_str
        response = self.get_model_response(content)
        assignee_dict = yaml.safe_load(response)

        current_datetime = datetime.now()

        assignee_list: List[Assignee] = []
        for assignee_name, tasks in assignee_dict.items():
            task_list: List[Task] = []
            for task_dict in tasks:
                delta = self.get_delta_time_from_str(task_dict["time"])
                task = Task(task_dict["task"], current_datetime + delta)
                task_list.append(task)
            
            assignee = Assignee(assignee_name, task_list)
            assignee_list.append(assignee)

        return assignee_list
    
    def generate_docx(self, conversation_str: str, template_path="docx_templates/default.docx"):
        assignees = self.generate_assignees(conversation_str)
        doc = self.get_docx_from_assignees(assignees, template_path)
        return doc
    
    def identify_assignee_names(self, conversation_str: str) -> dict:
        content = self.name_identification_prefix + conversation_str
        response = self.get_model_response(content)
        name_dict = yaml.safe_load(response)

        return name_dict
        
    
    def map_speaker_names(self, conversation_str: str):
        content = self.name_identification_prefix + conversation_str
        mapping_str = self.get_model_response(content)

        speakers = set(re.findall(r"\[-SPEAKER_\d+-\]", conversation_str))
        mapping = dict(re.findall(r"(\[-SPEAKER_\d+-\]):\s*(.*)", mapping_str))
        mapping = {speaker: name.strip() for speaker, name in mapping.items()}

        speakers_dict = {speaker: mapping.get(speaker, "Unknown") for speaker in speakers}

        return speakers_dict
    
    def add_task_table(self, doc, assignee):
        table = doc.add_table(rows=1, cols=2)
        table.style = 'EloquityTableStyle'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Задача'
        hdr_cells[1].text = 'Крайник срок'

        for task in assignee.tasks:
            row_cells = table.add_row().cells

            row_cells[0].text = task.content
            row_cells[1].paragraphs[0].paragraph_format.alignment = 1

            time = task.deadline.strftime("%H:%M") + "\n"
            date = task.deadline.strftime("%d.%m.%Y")

            run0 = row_cells[1].paragraphs[0].add_run(time)
            run0.font.size = Pt(16)

            run1 = row_cells[1].paragraphs[0].add_run(date)
            run1.font.size = Pt(12)

        doc.add_paragraph('\n')
    
    def get_docx_from_assignees(self, assignees, template_path="docx_templates/default.docx"):
        doc = Document(template_path)

        doc.add_heading('Задачи', 1)

        for assignee in assignees:
            doc.add_heading(assignee.name, 2)
            self.add_task_table(doc, assignee)

        return doc