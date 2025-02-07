
from dotenv import load_dotenv
import os
from src.eloquity_ai import EloquityAI
import json


if __name__ == "__main__":
    # with open("logs/transcribe_requests/dc749124-726b-4a11-881b-2537c2452937/log.json", encoding="utf-8") as file:
    # with open("logs/transcribe_requests/bb3fd104-87cb-41ef-b408-2ea355d02b34/log.json", encoding="utf-8") as file:
    #     log = json.load(file)
    # conversation = log["original_conversation"]
    # conversation = 'speaker_0:  Жене нужно доделать кота.'


    print("Starting...")
    load_dotenv()
    api_key = os.getenv("GPTUNNEL_API_KEY")

    with open("examples\data\conv_2_test.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = EloquityAI(api_key=api_key)

    json_log = dict()

    print("Generating docx...")
    doc = model.generate_docx(conversation, json_log=json_log)

    with open("tmp/json_log.json", "w", encoding="utf-8") as file:
        json.dump(json_log, file, indent=2, ensure_ascii=False)

    print("Saving the docx file as tasks.docx...")
    if doc is not None:
        doc.save('tasks.docx')
    else:
        print("Doc was None.")