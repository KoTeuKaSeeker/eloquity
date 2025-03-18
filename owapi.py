from src.chat_api.chat_api.openwebui_chat_api import OpenwebuiChatApi
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile
import shutil
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

upload_dir = "static"
os.makedirs(upload_dir, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}


@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    file_name = os.path.basename(file.filename)
    file_path = f"{upload_dir}/{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    download_url = f"http://localhost:8001/static/{file_name}"
    return {"filename": file.filename, "download_url": download_url}


if __name__ == "__main__":
    print("Helloooooo")
    openwebui_chat_api = OpenwebuiChatApi(app)
    openwebui_chat_api.start()
