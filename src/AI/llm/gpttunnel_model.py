from src.AI.llm.llm_interface import LLMInterface
import requests

class GptunnelModel(LLMInterface):
    api_key: str
    model_name: str
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://gptunnel.ru/v1/chat/completions"

    # def get_response(self, message: str, system_prompt: str = None) -> str:
    #     if system_prompt == None:
    #         system_prompt = self.system_prompt

    #     headers = {
    #         "Authorization": self.api_key,
    #         "Content-Type": "application/json"
    #     }

    #     messages = []
        
    #     if system_prompt is not None:
    #         messages.append({"role": "system", "content": system_prompt})
        
    #     messages.append({"role": "user", "content": message})

    #     data = {
    #         "model": self.model_name,
    #         "max_tokens": 2000,
    #         "messages": messages
    #     }

    #     response = requests.post(self.api_url, headers=headers, json=data)
    #     response.raise_for_status()  # Raise an error for HTTP errors
        
    #     content = response.json()["choices"][0]["message"]["content"]
    #     return content

    def get_response(self, messages: dict) -> dict:
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "max_tokens": 2000,
            "messages": messages
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for HTTP errors
        
        content = response.json()["choices"][0]["message"]["content"]

        message = {"role": "assistant", "content": content}

        return message