import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QMessageBox, QProgressBar, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Импортируем наши модули
from .data_loader import DataLoader
from .quality_engine import DataQualityEngine
from .report_gen import ReportGenerator

class DataQualityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Quality Assessment Tool")
        self.setMinimumSize(950, 650) # Немного увеличили окно для удобства

        self.main_font = QFont("Segoe UI", 10)
        self.title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        self.metric_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        QApplication.setFont(self.main_font)

        self.current_report = None
        self.file_path = "" # Инициализируем пустой путь
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- ВЕРХНЯЯ ПАНЕЛЬ (ЗАГОЛОВОК И ВЫБОР ФАЙЛА) ---
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Сервис аудита качества данных")
        title_label.setFont(self.title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()

        self.btn_select = QPushButton("📁 Выбрать CSV")
        self.btn_select.clicked.connect(self.select_file)
        header_layout.addWidget(self.btn_select)

        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        header_layout.addWidget(self.file_label)

        self.btn_run = QPushButton("🚀 Запустить аудит")
        self.btn_run.setStyleSheet("background-color: #2b579a; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self.run_analysis)
        header_layout.addWidget(self.btn_run)

        main_layout.addLayout(header_layout)

        # --- ЦЕНТРАЛЬНАЯ ЧАСТЬ (ВКЛАДКИ) ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Вкладка 1: Сводка
        self.tab_summary = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.tab_summary, "📊 Сводка")

        # Вкладка 2: Детали ошибок
        self.tab_issues = QWidget()
        self.setup_issues_tab()
        self.tabs.addTab(self.tab_issues, "⚠️ Найденные ошибки")

        # --- НИЖНЯЯ ПАНЕЛЬ (СТАТУС И ЭКСПОРТ) ---
        footer_layout = QHBoxLayout()
        
        self.status_label = QLabel("Готов к работе")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()

        self.btn_export_json = QPushButton("💾 Сохранить JSON")
        self.btn_export_json.setEnabled(False)
        self.btn_export_json.clicked.connect(lambda: self.export_report("json"))
        footer_layout.addWidget(self.btn_export_json)

        self.btn_export_excel = QPushButton("📈 Сохранить Excel")
        self.btn_export_excel.setEnabled(False)
        self.btn_export_excel.clicked.connect(lambda: self.export_report("excel"))
        footer_layout.addWidget(self.btn_export_excel)

        main_layout.addLayout(footer_layout)

    def setup_summary_tab(self):
        layout = QVBoxLayout(self.tab_summary)
        grid = QGridLayout()
        
        self.lbl_total_rows = self.create_metric_card("Всего строк", "0")
        grid.addWidget(self.lbl_total_rows, 0, 0)
        
        self.lbl_total_errors = self.create_metric_card("Найдено проблем", "0")
        grid.addWidget(self.lbl_total_errors, 0, 1)
        
        self.lbl_quality_score = self.create_metric_card("Quality Score", "0%")
        grid.addWidget(self.lbl_quality_score, 1, 0)
        
        self.lbl_completeness = self.create_metric_card("Completeness", "0%")
        grid.addWidget(self.lbl_completeness, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def create_metric_card(self, title, value):
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        layout = QVBoxLayout()
        lbl_value = QLabel(value)
        lbl_value.setFont(self.metric_font)
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_value)
        group.setLayout(layout)
        return group

    def setup_issues_tab(self):
        layout = QVBoxLayout(self.tab_issues)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Тип", "Колонка", "Критичность", "Описание", "Кол-во"])
        
        # Настройка ширины колонок (Описание забирает всё свободное место)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Включаем перенос текста на новую строку и автоподстройку высоты строк
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с данными", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: black; font-weight: bold;")
            self.btn_run.setEnabled(True)
            self.status_label.setText("Файл выбран. Нажмите 'Запустить аудит'.")

    def run_analysis(self):
        if not self.file_path:
            return

        self.status_label.setText("Анализ данных... Пожалуйста, подождите.")
        self.btn_run.setEnabled(False)
        self.btn_select.setEnabled(False)
        
        try:
            df = DataLoader.load_csv(self.file_path)
            engine = DataQualityEngine(df)
            self.current_report = engine.run_all()
            
            self.update_ui_with_report(self.current_report)
            
            self.status_label.setText("✅ Анализ успешно завершен!")
            self.tabs.setCurrentIndex(0)
            
            self.btn_export_json.setEnabled(True)
            self.btn_export_excel.setEnabled(True)

        except Exception as e:
            self.status_label.setText("❌ Ошибка при обработке")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")
        finally:
            self.btn_run.setEnabled(True)
            self.btn_select.setEnabled(True)

    def update_ui_with_report(self, report):
        # Обновляем карточки
        self.lbl_total_rows.findChild(QLabel).setText(str(report.total_rows))
        self.lbl_total_errors.findChild(QLabel).setText(str(int(report.metrics['total_errors_found'])))
        self.lbl_quality_score.findChild(QLabel).setText(f"{report.metrics['quality_score']}%")
        self.lbl_completeness.findChild(QLabel).setText(f"{report.metrics['completeness_score']}%")

        # Очищаем и заполняем таблицу
        self.table.setRowCount(len(report.issues))
        for row, issue in enumerate(report.issues):
            self.table.setItem(row, 0, QTableWidgetItem(issue.check_type))
            self.table.setItem(row, 1, QTableWidgetItem(issue.column))
            
            severity_item = QTableWidgetItem(issue.severity)
            if issue.severity == 'high':
                severity_item.setBackground(QColor("#ffcccc"))
            elif issue.severity == 'medium':
                severity_item.setBackground(QColor("#ffe5cc"))
            else:
                severity_item.setBackground(QColor("#e5ffcc"))
            self.table.setItem(row, 2, severity_item)
            
            # Добавляем описание и всплывающую подсказку (ToolTip)
            desc_item = QTableWidgetItem(issue.message)
            desc_item.setToolTip(issue.message)
            self.table.setItem(row, 3, desc_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(str(issue.count)))

    def export_report(self, format_type):
        if not self.current_report:
            return
            
        if format_type == "json":
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить JSON", "dq_report.json", "JSON (*.json)")
            if file_path:
                ReportGenerator.save_json(self.current_report, file_path)
                self.status_label.setText(f"JSON сохранен: {os.path.basename(file_path)}")
        elif format_type == "excel":
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить Excel", "dq_report.xlsx", "Excel (*.xlsx)")
            if file_path:
                ReportGenerator.save_excel(self.current_report, file_path)
                self.status_label.setText(f"Excel сохранен: {os.path.basename(file_path)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataQualityApp()
    window.show()
    sys.exit(app.exec())