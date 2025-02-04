import requests
import re
from datetime import datetime
from typing import List
import yaml

class Task:
    def __init__(self, content: str, deadline: str):
        self.content = content
        # self.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
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
    
    def generate_raw_task_str(self, conversation_str: str) -> str:
        content = self.task_assigment_prefix + conversation_str
        task_str = self.get_model_response(content)

        return task_str
    
    def generate_assignees(self, conversation_str: str) -> List[Assignee]:
        content = self.task_assigment_prefix + conversation_str
        response = self.get_model_response(content)
        assignee_dict = yaml.safe_load(response)

        name_dict = self.identify_assignee_names(conversation_str)

        assignee_list: List[Assignee] = []
        for assignee_name, tasks in assignee_dict.items():
            task_list: List[Task] = []
            for task_dict in tasks:
                task = Task(task_dict["task"], task_dict["time"])
                task_list.append(task)
            
            assignee = Assignee(name_dict[assignee_name], task_list)
            assignee_list.append(assignee)

        return assignee_list
    
    def identify_assignee_names(self, conversation_str: str) -> dict:
        content = self.name_identification_prefix + conversation_str
        response = self.get_model_response(content)
        name_dict = yaml.safe_load(response)

        return name_dict

    def extract_assignees(self, raw_task_str: str) -> Assignee:
        # task_str = self.generate_raw_task_str(conversation_str)

        speakers = dict(re.findall(r"(\[-SPEAKER_\d+-\]):\s*(.*)", raw_task_str))

        assignees: List[Assignee] = []
        for speaker_name, tasks in speakers.items():
            task_pattern = r"\[TIME: '(.*?)'\]\s*(.*)"
            tasks_found = re.findall(task_pattern, tasks)

            task_list: List[Task] = []
            for time, task in tasks_found:
                task = Task(task.strip(), time)
                task_list.append(task)
            
            assignee = Assignee(speaker_name, task_list)
            assignees.append(assignee)

        return assignees
        
    
    def map_speaker_names(self, conversation_str: str):
        content = self.name_identification_prefix + conversation_str
        mapping_str = self.get_model_response(content)

        speakers = set(re.findall(r"\[-SPEAKER_\d+-\]", conversation_str))
        mapping = dict(re.findall(r"(\[-SPEAKER_\d+-\]):\s*(.*)", mapping_str))
        mapping = {speaker: name.strip() for speaker, name in mapping.items()}

        speakers_dict = {speaker: mapping.get(speaker, "Unknown") for speaker in speakers}

        return speakers_dict
    
    def generate_tasks_and_assign_names(self, conversation_str: str, speakers_dict: dict):
        content = self.task_assigment_prefix + conversation_str

        mapping_str = self.get_model_response(content)

        def replace(match):
            speaker_tag = match.group(0)
            return speakers_dict.get(speaker_tag, speaker_tag)
        
        tasks_str = re.sub(r"\[-SPEAKER_\d+-\]", replace, mapping_str)

        return tasks_str
    
    def generate_task_string(self, conversation_str: str) -> str:
        speakers_dict = self.map_speaker_names(conversation_str)
        tasks_str = self.generate_tasks_and_assign_names(conversation_str, speakers_dict)

        return tasks_str