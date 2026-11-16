import os
import pandas as pd
from .data_loader import DataLoader
from .quality_engine import DataQualityEngine
from .report_gen import ReportGenerator

def run_prototype():
    print("\n" + "="*50)
    print("🚀 СЕРВИС АУДИТА КАЧЕСТВА ДАННЫХ (DATA QUALITY СONSOLE)")
    print("="*50)
    
    # Запрашиваем путь к файлу у пользователя
    file_path = input("👉 Введите путь к вашему CSV-файлу (например, data.csv): ").strip()
    
    # Очищаем кавычки, если пользователь просто перетащил файл в терминал
    file_path = file_path.strip("'\"")

    if not os.path.exists(file_path):
        print(f"❌ Ошибка: Файл по пути '{file_path}' не найден!")
        print("Пожалуйста, проверьте правильность пути и повторите попытку.")
        return

    if not file_path.endswith('.csv'):
        print("❌ Ошибка: На данном этапе поддерживаются только файлы формата .csv")
        return

    try:
        # Шаг 1: Загрузка данных
        df = DataLoader.load_csv(file_path)
        print(f"✅ Файл успешно загружен. Размерность: {len(df)} строк, {len(df.columns)} колонок.")
        
        # Шаг 2: Анализ качества (универсальный, для любых колонок)
        print("🔍 Запуск сканирования на пропуски и дубликаты...")
        engine = DataQualityEngine(df)
        report = engine.run_all()
        
        # Шаг 3: Сохранение отчетов
        print("📊 Компиляция аналитических отчетов...")
        ReportGenerator.save_json(report, "dq_report.json")
        ReportGenerator.save_excel(report, "dq_report.xlsx")
        
        print("="*50)
        print("🎉 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print(f"📁 JSON-лог сохранен в: {os.path.abspath('dq_report.json')}")
        print(f"📁 Бизнес-отчет сохранен в: {os.path.abspath('dq_report.xlsx')}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Произошла критическая ошибка при обработке файла: {e}")

if __name__ == "__main__":
    run_prototype()
