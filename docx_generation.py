
from dotenv import load_dotenv
import os
from src.eloquity_ai import EloquityAI


if __name__ == "__main__":
    print("Starting...")
    load_dotenv()
    api_key = os.getenv("API_KEY")

    with open("examples/data/conv_0.txt", "r", encoding="utf-8") as file:
        conversation = file.read()

    model = EloquityAI(api_key=api_key)

    print("Generating docx...")
    doc = model.generate_docx(conversation)

    print("Saving the docx file as tasks.docx...")
    doc.save('tasks.docx')