from fastapi import FastAPI
from src.openwebui_coordinator.tasks import router as tasks_router
import uvicorn

app = FastAPI()

app.include_router(tasks_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)