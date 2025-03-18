from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from dataclasses import dataclass

# Task Dataclass
@dataclass
class Task:
    task_id: str
    user_id: str
    initial_message: str
    initial_files: List[str]
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

# Pydantic Models for Request and Response
class CreateTaskRequest(BaseModel):
    user_id: str
    message: str
    files: List[str] = []

class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    initial_message: str
    initial_files: List[str]
    status: str
    output_messages: List[str] = []
    output_files: List[str] = []

# Create the router
router = APIRouter()

# 1. POST /task/create
@router.post("/task/create", response_model=TaskResponse)
async def create_task(request: CreateTaskRequest):
    task_id = str(uuid4())  # Generate a unique task ID
    task = Task(
        task_id=task_id,
        user_id=request.user_id,
        initial_message=request.message,
        initial_files=request.files,
        status="Pending",  # Default status
    )
    tasks_db[task_id] = task

    print("All task messages:")
    for task in tasks_db.values():
        print(f"    {task.initial_message}")

    return TaskResponse(
        task_id=task_id,
        user_id=task.user_id,
        initial_message=task.initial_message,
        initial_files=task.initial_files,
        status=task.status,
        output_messages=task.output_messages,
        output_files=task.output_files
    )

# 2. GET /tasks/{user_id}
@router.get("/tasks/{user_id}", response_model=dict)
async def get_tasks(user_id: str):
    user_tasks = [task for task in tasks_db.values() if task.user_id == user_id]

    print("All task messages:")
    for task in tasks_db.values():
        print(f"    {task.initial_message}")

    print("\nUser task messages:")
    for task in user_tasks:
        print(f"    {task.initial_message}")

    task_dict_list = [task.__dict__ for task in user_tasks]

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
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return TaskResponse(
        task_id=task_id,
        user_id=task.user_id,
        initial_message=task.initial_message,
        initial_files=task.initial_files,
        status=task.status,
        output_messages=task.output_messages,
        output_files=task.output_files
    )

# 6. POST /task/{task_id}/upload_file
# @router.post("/task/{task_id}/upload_file")
# async def upload_file(task_id: str, file: str):
#     task = tasks_db.get(task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found.")
#     task.output_files.append(file)
#     return {"task_id": task_id, "file_url": file}
