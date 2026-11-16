@echo off
chcp 65001 >nul
title Data Quality Tool

echo ========================================
echo   Data Quality Tool - запуск
echo ========================================
echo.

cd /d "%~dp0"

if not exist "backend-python\venv\Scripts\python.exe" (
    echo [ОШИБКА] Не найден venv в backend-python\venv
    echo Создай его: python -m venv backend-python\venv
    pause
    exit /b 1
)

echo [1/2] Запуск Backend (FastAPI)...
start "Backend API" cmd /k "cd /d "%~dp0backend-python" && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Запуск Frontend (React)...
start "Frontend" cmd /k "cd /d "%~dp0Practic" && npm run dev -- --host"

timeout /t 5 /nobreak >nul
echo.
echo Открываю сайт...
start http://localhost:5173

echo.
echo ========================================
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   API docs: http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Окна Backend и Frontend можно свернуть.
echo Чтобы остановить - закрой оба окна или нажми Ctrl+C в них.
echo.
pause