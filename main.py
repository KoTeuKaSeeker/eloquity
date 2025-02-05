
from dotenv import load_dotenv
import os
from src.eloquity_ai import EloquityAI


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")

    with open("examples/data/conv_0.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = EloquityAI(api_key=api_key)

    assignees = model.generate_assignees(conversation)

    for assignee in assignees:
        print(assignee)