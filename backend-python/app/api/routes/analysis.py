from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas.analysis import AnalysisRequest, SuggestRequest
from app.schemas.report import Report
from app.services.analysis_service import run_data_analysis, suggest_file_rules
from app.services.task_service import (
    create_task,
    update_task,
    get_task,
    TaskStatus
)

router = APIRouter()


import threading
import time

def run_analysis_in_background(task_id: str, request: AnalysisRequest):
    stop_progress = threading.Event()

    def fake_progress():
        """Плавно двигает прогресс, пока идёт реальная проверка"""
        current = 10
        stages = [
            (20, "Читаем файл..."),
            (35, "Определяем правила..."),
            (50, "Ищем пропуски..."),
            (65, "Ищем дубликаты..."),
            (80, "Проверяем значения..."),
            (90, "Формируем отчёт..."),
        ]
        
        for target, message in stages:
            if stop_progress.is_set():
                return
            while current < target:
                if stop_progress.is_set():
                    return
                current += 1
                update_task(task_id, progress=current, message=message)
                time.sleep(0.25)  # скорость роста прогресса
            time.sleep(0.3)

    try:
        update_task(task_id, status=TaskStatus.RUNNING, progress=5, message="Начинаем проверку...")

        # Запускаем "живой" прогресс в отдельном потоке
        progress_thread = threading.Thread(target=fake_progress, daemon=True)
        progress_thread.start()

        # Реальная проверка
        report = run_data_analysis(request)

        # Останавливаем имитацию и ставим 100%
        stop_progress.set()
        progress_thread.join(timeout=1)

        update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            message="Проверка завершена",
            report=report.model_dump()
        )
    except Exception as e:
        stop_progress.set()
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


@router.post("/suggest-rules")
def suggest_rules(request: SuggestRequest):
    return suggest_file_rules(request.dataset_id)