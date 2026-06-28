import asyncio
import uuid


tasks = {}


def create_task(message):
    task_id = str(uuid.uuid4())

    tasks[task_id] = {
        "message": message,
        "cancel_event": asyncio.Event(),
        "status": "waiting",
        "file_path": None,
    }

    return task_id


def get_task(task_id):
    return tasks.get(task_id)


def cancel_task(task_id):
    task = tasks.get(task_id)

    if task:
        task["cancel_event"].set()


def is_cancelled(task_id):
    task = tasks.get(task_id)

    if not task:
        return False

    return task["cancel_event"].is_set()


def remove_task(task_id):
    tasks.pop(task_id, None)