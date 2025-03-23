from fastapi import FastAPI
from src.openwebui_coordinator.tasks import router as tasks_router
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI()

upload_dir = "static"
os.makedirs(upload_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=upload_dir), name=upload_dir)

app.include_router(tasks_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)