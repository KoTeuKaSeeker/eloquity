
from dotenv import load_dotenv
import os
from src.eloquity_ai import EloquityAI


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")

    with open("conversation.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = EloquityAI(api_key=api_key)
    tasks_str = model.generate_task_string(conversation)
    
    print(tasks_str)