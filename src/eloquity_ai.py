import requests
import re


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

    def get_model_response(self, messages):
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "max_tokens": 2000,
            "messages": messages
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        content = response.json()["choices"][0]["message"]["content"]

        return {"role": "assistant", "content": content}
    
    def map_speaker_names(self, conversation_str: str):
        content = self.name_identification_prefix + conversation_str

        messages = [
            {"role": "user", "content": content}
        ]
 
        mapping_str = self.get_model_response(messages)['content']

        speakers = set(re.findall(r"\[-SPEAKER_\d+-\]", conversation_str))
        mapping = dict(re.findall(r"(\[-SPEAKER_\d+-\]):\s*(.*)", mapping_str))
        mapping = {speaker: name.strip() for speaker, name in mapping.items()}

        speakers_dict = {speaker: mapping.get(speaker, "Unknown") for speaker in speakers}

        return speakers_dict
    
    def generate_tasks_and_assign_names(self, conversation_str: str, speakers_dict: dict):
        content = self.task_assigment_prefix + conversation_str

        messages = [
            {"role": "user", "content": content}
        ]

        mapping_str = self.get_model_response(messages)['content']

        def replace(match):
            speaker_tag = match.group(0)
            return speakers_dict.get(speaker_tag, speaker_tag)
        
        tasks_str = re.sub(r"\[-SPEAKER_\d+-\]", replace, mapping_str)

        return tasks_str
    
    def generate_task_string(self, conversation_str: str) -> str:
        speakers_dict = self.map_speaker_names(conversation_str)
        tasks_str = self.generate_tasks_and_assign_names(conversation_str, speakers_dict)

        return tasks_str