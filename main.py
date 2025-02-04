import requests
import re
from dotenv import load_dotenv
import os


class TempModel:
    def __init__(self, api_key: str):
        self.api_key = api_key

        with open("prefixes/name_identification.txt", "r", encoding="utf-8") as file:
            self.name_identification_prefix = file.read()

        with open("prefixes/task_assigment.txt", "r", encoding="utf-8") as file:
            self.task_assigment_prefix = file.read()

    def complete(self, messages):
        url = "https://gptunnel.ru/v1/chat/completions"
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
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        content = response.json()["choices"][0]["message"]["content"]

        return {"role": "assistant", "content": content}
    
    def identify_names(self, conversation_str: str):
        content = self.name_identification_prefix + conversation_str

        messages = [
            {"role": "user", "content": content}
        ]
 
        mapping_str = self.complete(messages)['content']

        speakers = set(re.findall(r"\[-SPEAKER_\d+-\]", conversation_str))
        mapping = dict(re.findall(r"(\[-SPEAKER_\d+-\]):\s*(.*)", mapping_str))
        mapping = {speaker: name.strip() for speaker, name in mapping.items()}

        speakers_dict = {speaker: mapping.get(speaker, "Unknown") for speaker in speakers}

        return speakers_dict
    
    def assign_tasks(self, conversation_str: str, speakers_dict: dict):
        content = self.task_assigment_prefix + conversation_str

        messages = [
            {"role": "user", "content": content}
        ]

        mapping_str = self.complete(messages)['content']

        def replace(match):
            speaker_tag = match.group(0)
            return speakers_dict.get(speaker_tag, speaker_tag)
        
        tasks_str = re.sub(r"\[-SPEAKER_\d+-\]", replace, mapping_str)

        return tasks_str
    
    def generate_tasks(self, conversation_str: str) -> str:
        speakers_dict = self.identify_names(conversation_str)
        tasks_str = self.assign_tasks(conversation_str, speakers_dict)

        return tasks_str


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("API_KEY")

    with open("conversation.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = TempModel(api_key=api_key)

    tasks_str = model.generate_tasks(conversation)
    
    print(tasks_str)