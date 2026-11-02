import os
import pandas as pd
from .data_loader import DataLoader
from .quality_engine import DataQualityEngine
from .report_gen import ReportGenerator

def run_prototype():
    print("=== Запуск прототипа DQ ===")
    
    # Генерация временного тестового файла с ошибками
    mock_data = {
        "id":1,
        "name": ["Иван", "Анна", "Анна", None, "Петр"],
        "age": [25, 30, 30, 40, None]
    }
    mock_file = "demo_dirty_data.csv"
    pd.DataFrame(mock_data).to_csv(mock_file, index=False)

    # Выполнение конвейера
    df = DataLoader.load_csv(mock_file)
    engine = DataQualityEngine(df)
    report = engine.run_all()
    
    ReportGenerator.save_json(report)
    ReportGenerator.save_excel(report)
    
    if os.path.exists(mock_file):
        os.remove(mock_file)
    print("=== Анализ завершен ===")

if __name__ == "__main__":
    run_prototype()