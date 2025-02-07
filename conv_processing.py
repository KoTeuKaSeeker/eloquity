
from dotenv import load_dotenv
import os
from src.eloquity_ai import EloquityAI
import json


if __name__ == "__main__":
    print("Starting...")
    load_dotenv()
    api_key = os.getenv("GPTUNNEL_API_KEY")

    with open("examples/data/conv_0.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = EloquityAI(api_key=api_key)

    json_log = dict()

    print("Generating docx...")
    doc = model.generate_docx(conversation, json_log=json_log)

    with open("tmp/json_log.json", "w", encoding="utf-8") as file:
        json.dump(json_log, file, indent=2, ensure_ascii=False)

    print("Saving the docx file as tasks.docx...")
    doc.save('tasks.docx')