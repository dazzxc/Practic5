import os

from .data_loader import DataLoader
from .quality_engine import DataQualityEngine
from .report_gen import ReportGenerator


def run_prototype():
    print("\n" + "="*50)
    print("Проверка качества данных (консольная версия)")
    print("="*50)

    file_path = input("Путь к CSV-файлу (например, data.csv): ").strip()

    # убираем кавычки
    file_path = file_path.strip("'\"")

    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        print("Проверьте путь и попробуйте ещё раз.")
        return

    if not file_path.endswith('.csv'):
        print("Пока умеем только .csv")
        return

    try:
        df = DataLoader.load_csv(file_path)
        print(f"Загружено: {len(df)} строк, {len(df.columns)} колонок")

        print("Проверяем...")
        engine = DataQualityEngine(df)
        report = engine.run_all()

        print("Сохраняем отчёты...")
        ReportGenerator.save_json(report, "dq_report.json")
        ReportGenerator.save_excel(report, "dq_report.xlsx")

        print("="*50)
        print("Готово!")
        print(f"JSON: {os.path.abspath('dq_report.json')}")
        print(f"Excel: {os.path.abspath('dq_report.xlsx')}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"Что-то пошло не так: {e}")


if __name__ == "__main__":
    run_prototype()
