from open_webui.config import UPLOAD_DIR
from pydantic import BaseModel, Field
from typing import Optional
import requests
import random
import time
import re
import os


class Pipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="")
        OPENWEBUI_COORDINATOR_PORT: str = Field(default="8001")

    def __init__(self):
        self.file_handler = True  # Enable custom file handling logic
        self.valves = self.Valves()
        self.uploaded_files = {}

    def create_task(self, user_id, chat_id, message, files):
        url = f"http://host.docker.internal:{self.valves.OPENWEBUI_COORDINATOR_PORT}/task/create"

        # Data to send with the request
        data = {"user_id": str(user_id), "chat_id": str(chat_id), "message": message}

        # Send the POST request to the endpoint
        response = requests.post(url, data=data, files=files)

        return response.json()

    def get_task(self, task_id):
        BASE_URL = f"http://host.docker.internal:{self.valves.OPENWEBUI_COORDINATOR_PORT}"  # Update if using a different host/port
        # Send GET request
        response = requests.get(f"{BASE_URL}/task/{task_id}")
        print(f"TASK[{task_id}]:\n{response.json()}")

        # Send the GET request to the endpoint
        return response.json()

    def get_uploaded_file(self, __files__: dict):
        uploaded_file = None
        if __files__ is not None:
            for file in __files__:
                if file["file"]["id"] not in self.uploaded_files:
                    self.uploaded_files[file["file"]["id"]] = file
                    uploaded_file = file
        return uploaded_file

    def get_files_dict_from_uploaded_file(self, uploaded_file):
        file_path = os.path.join(
            UPLOAD_DIR,
            uploaded_file["file"]["id"] + "_" + uploaded_file["file"]["filename"],
        )

        # with open(file_path, "rb") as f:
        files = {"file": (file_path, open(file_path, "rb"), "audio/mpeg")}

        return files

    def wait_for_task_completion(self, task_id: str):
        while True:
            task = self.get_task(task_id)
            if task["status"] == "Done":
                return task
            time.sleep(3)
            # output_str = "NOTHING"
            # # for message in task["output_messages"]:
            # #     output_str += message + "\n"
            # # output_str += str(task)
            # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
            # print(task)

            # for message in task["output_messages"]:
            #     output_str += str(message)
            # print(output_str)
            # # return str(output_str)
            # return str(task["output_messages"])

    def pipe(self, body: dict, __files__: dict, __metadata__: dict):
        if body["stream"]:
            try:
                uploaded_file = self.get_uploaded_file(__files__)
                files = []
                if uploaded_file is not None:
                    files = self.get_files_dict_from_uploaded_file(uploaded_file)

                user_messaage = body["messages"][-1]["content"]

                user_id = __metadata__["chat_id"]
                chat_id = __metadata__["chat_id"]
                json_response = self.create_task(user_id, chat_id, user_messaage, files)

                task = self.wait_for_task_completion(json_response["task_id"])

                output_message = "\n\n".join(task["output_messages"])
                if len(output_message) == 0:
                    return "..."

                return output_message

                # return "The task was completed! Yayyy! :D"

                # while True:
                #     task = self.get_task(task_id)
                #     if task["status"] == "Done":
                #         output_str = "NOTHING"
                #         # for message in task["output_messages"]:
                #         #     output_str += message + "\n"
                #         # output_str += str(task)
                #         print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
                #         print(task)
                #         for message in task["output_messages"]:
                #             output_str += str(message)
                #         print(output_str)
                #         # return str(output_str)
                #         return str(task["output_messages"])
                #     time.sleep(3)

                return str(json_response)

                if uploaded_file is not None:
                    return "FILE HANDLING"
                else:
                    return "TEXT HANDLING"
            except Exception as e:
                return str(e)
            return "How did you get here?"
        else:
            return "SOME OTHER TASK!!!!"
