from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Хранилище задач в памяти
tasks: Dict[str, Dict[str, Any]] = {}


def create_task() -> str:
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "progress": 0,
        "message": "Ожидание запуска",
        "report": None,
        "error": None,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    return task_id


def update_task(
    task_id: str,
    status: Optional[TaskStatus] = None,
    progress: Optional[int] = None,
    message: Optional[str] = None,
    report: Optional[dict] = None,
    error: Optional[str] = None
):
    if task_id not in tasks:
        return

    task = tasks[task_id]
    
    if status is not None:
        task["status"] = status
    if progress is not None:
        task["progress"] = max(0, min(100, progress))
    if message is not None:
        task["message"] = message
    if report is not None:
        task["report"] = report
    if error is not None:
        task["error"] = error
        
    task["updated_at"] = datetime.now().isoformat(timespec="seconds")


def get_task(task_id: str) -> Optional[dict]:
    return tasks.get(task_id)