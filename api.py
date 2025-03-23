import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
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
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
