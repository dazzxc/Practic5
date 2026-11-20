from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas.analysis import AnalysisRequest
from app.schemas.report import Report
from app.services.analysis_service import run_data_analysis
from app.services.task_service import (
    create_task,
    update_task,
    get_task,
    TaskStatus
)

router = APIRouter()


def run_analysis_in_background(task_id: str, request: AnalysisRequest):
    try:
        print(f"[TASK {task_id}] Старт проверки")
        update_task(task_id, status=TaskStatus.RUNNING, progress=10, message="Идёт проверка...")

        report = run_data_analysis(request)

        print(f"[TASK {task_id}] Проверка успешно завершена")
        update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            message="Проверка завершена",
            report=report.model_dump()
        )
    except Exception as e:
        print(f"[TASK {task_id}] ОШИБКА: {e}")
        update_task(
            task_id,
            status=TaskStatus.FAILED,
            progress=100,
            message="Ошибка при проверке",
            error=str(e)
        )

@router.post("/run-check")
def run_check(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = create_task()
    
    # Запускаем тяжёлую работу в фоне
    background_tasks.add_task(run_analysis_in_background, task_id, request)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Проверка запущена"
    }


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task