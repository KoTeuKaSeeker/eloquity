from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Query
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from dataclasses import dataclass
import socket
import shutil
import os

# Task Dataclass
@dataclass
class Task:
    task_id: str
    user_id: str
    chat_id: str
    model_name: str
    initial_message: str
    initial_file: str
    status: str
    output_messages: Optional[List[str]] = None
    output_files: Optional[List[str]] = None

    def __post_init__(self):
        if self.output_messages is None:
            self.output_messages = []
        if self.output_files is None:
            self.output_files = []

# Create a dictionary to store tasks
tasks_db = {}
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
SERVER_LOCAL_HOST = "localhost"

# Pydantic Models for Request and Response
class CreateTaskRequest(BaseModel):
    user_id: str
    message: str
    files: List[str] = []

class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    chat_id: str
    model_name: str
    initial_message: str
    initial_file: str
    status: str
    output_messages: List[str] = []
    output_files: List[str] = []

# Create the router
router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": 200, "message": "The OpenWebUI Coordinator is in good health and ready to accept tasks."}

# 1. POST /task/create
@router.post("/task/create")
async def create_task(user_id: str = Form(...), 
                      chat_id: str = Form(...), 
                      model_name: str = Form(...), 
                      message: str = Form(...), 
                      file: Optional[UploadFile] = File(None)):
    file_url = ""
    if file is not None:
        file_url = upload_file(file)
    
    task_id = str(uuid4())  # Generate a unique task ID
    task = Task(
        task_id=task_id,
        user_id=user_id,
        chat_id=chat_id,
        model_name=model_name,
        initial_message=message,
        initial_file=file_url,
        status="Pending",  # Default status
    )
    tasks_db[task_id] = task

    
    # print("All task messages:")
    # for task in tasks_db.values():
    #     print(f"    {task.initial_message}")

    return TaskResponse(
        task_id=task_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        model_name=task.model_name,
        initial_message=task.initial_message,
        initial_file=task.initial_file,
        status=task.status,
        output_messages=task.output_messages,
        output_files=task.output_files
    )

@router.post("/task/modify")
async def modify_task(task_id: str = Form(...), user_id: str = Form(...), chat_id: str = Form(...), message: str = Form(...), file: Optional[UploadFile] = File(None)):
    file_url = ""
    if file is not None:
        file_url = upload_file(file)
    
    # task_id = str(uuid4())  # Generate a unique task ID
    # task = Task(
    #     task_id=task_id,
    #     user_id=user_id,
    #     initial_message=message,
    #     initial_file=file_url,
    #     status="Pending",  # Default status
    # )
    task: Task = tasks_db[task_id]

    task.user_id = user_id
    task.chat_id = chat_id
    task.initial_message = message
    task.initial_file = file_url

    
    # print("All task messages:")
    # for task in tasks_db.values():
    #     print(f"    {task.initial_message}")

    return TaskResponse(
        task_id=task_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        model_name=task.model_name,
        initial_message=task.initial_message,
        initial_file=task.initial_file,
        status=task.status,
        output_messages=task.output_messages,
        output_files=task.output_files
    )


# 2. GET /tasks/{user_id}
@router.get("/tasks", response_model=dict)
async def get_tasks(user_id: Optional[str] = Query(None)):
    
    tasks = tasks_db.values()
    if user_id is not None:
        tasks = [task for task in tasks_db.values() if task.user_id == user_id]

    # print("All task messages:")
    # for task in tasks_db.values():
    #     print(f"    {task.initial_message}")

    # print("\nUser task messages:")
    # for task in user_tasks:
    #     print(f"    {task.initial_message}")


    task_dict_list = [task.__dict__ for task in tasks]

    return {"status": 200, "tasks": task_dict_list}


# 3. POST /task/{task_id}/add_message
@router.post("/task/{task_id}/add_message", response_model=dict)
async def add_message(task_id: str, message: str):
    task: Task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.output_messages.append(message)
    return {"task_id": task_id, "message": message}

# 4. POST /task/{task_id}/update_status
@router.post("/task/{task_id}/update_status", response_model=dict)
async def update_status(task_id: str, status: str):
    task: Task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.status = status
    return {"task_id": task_id, "new_status": status}

# 5. GET /task/{task_id}
@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task: Task = tasks_db.get(task_id)
    print(f"TASK[{task_id}]:\n{task}")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return TaskResponse(
        task_id=task_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        model_name=task.model_name,
        initial_message=task.initial_message,
        initial_file=task.initial_file,
        status=task.status,
        output_messages=task.output_messages,
        output_files=task.output_files
    )


def upload_file(file: UploadFile):
    file_ext = os.path.splitext(os.path.basename(file.filename))[1]
    file_name = str(uuid4()) + file_ext
    file_path = f"static/{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/static/{file_name}"

    return url



# 6. POST /task/{task_id}/upload_file
@router.post("/task/{task_id}/upload_file")
async def upload_file_in_task(task_id: str, file: UploadFile = File(...)):
    task: Task = tasks_db.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    file_ext = os.path.splitext(os.path.basename(file.filename))[1]
    file_name = str(uuid4()) + file_ext
    file_path = f"static/{file_name}" 

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    download_url = f"http://{SERVER_LOCAL_HOST}:{SERVER_PORT}/static/{file_name}"

    task.output_files.append(download_url)
    task.output_messages.append(download_url)
    return {"task_id": task_id, "file_url": download_url}