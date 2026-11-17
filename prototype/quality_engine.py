import pandas as pd
from datetime import datetime
from .schemas import Issue, QualityReport


class DataQualityEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.issues = []
        self.total_rows = len(df)

    def check_missing(self):
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                samples = self.df[self.df[col].isna()].head(3).to_dict(orient='records')
                clean_samples = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in samples]
                self.issues.append(Issue(
                    check_type="missing_values",
                    column=col,
                    severity="medium" if (missing_count / self.total_rows) < 0.2 else "high",
                    message=f"Обнаружено {missing_count} пропущенных значений в '{col}'",
                    count=int(missing_count),
                    sample=clean_samples
                ))

    def check_duplicates(self):
        dup_mask = self.df.duplicated(keep=False)
        dup_count = dup_mask.sum()
        if dup_count > 0:
            samples = self.df[dup_mask].head(3).to_dict(orient='records')
            self.issues.append(Issue(
                check_type="duplicates",
                column="ALL",
                severity="high",
                message="Обнаружены полные дубликаты строк",
                count=int(dup_count),
                sample=[{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in samples]
            ))

    # завершение не раньше создания
    def check_date_consistency(self):
        # если колонки есть
        if 'created_at' in self.df.columns and 'completed_at' in self.df.columns:
            # кривые -> NaT
            created = pd.to_datetime(self.df['created_at'], errors='coerce')
            completed = pd.to_datetime(self.df['completed_at'], errors='coerce')

            # без пустых
            invalid_mask = (completed < created) & created.notna() & completed.notna()
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                samples = self.df[invalid_mask].head(3).to_dict(orient='records')
                clean_samples = [{k: (None if pd.isna(v) else str(v)) for k, v in r.items()} for r in samples]
                self.issues.append(Issue(
                    check_type="date_inconsistency",
                    column="created_at, completed_at",
                    severity="high",
                    message=f"Нарушена логика дат: 'completed_at' раньше 'created_at' ({invalid_count} раз)",
                    count=int(invalid_count),
                    sample=clean_samples
                ))

    # сумма >= 0
    def check_invalid_values(self):
        if 'amount' in self.df.columns:
            # текст -> NaN
            amounts = pd.to_numeric(self.df['amount'], errors='coerce')
            negative_mask = amounts < 0
            negative_count = negative_mask.sum()

            if negative_count > 0:
                samples = self.df[negative_mask].head(3).to_dict(orient='records')
                clean_samples = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in samples]
                self.issues.append(Issue(
                    check_type="invalid_value",
                    column="amount",
                    severity="high",
                    message=f"Обнаружено {negative_count} отрицательных значений в колонке 'amount'",
                    count=int(negative_count),
                    sample=clean_samples
                ))

    def run_all(self) -> QualityReport:
        self.check_missing()
        self.check_duplicates()
        self.check_date_consistency()
        self.check_invalid_values()

        # полнота
        total_cells = self.total_rows * len(self.df.columns)
        total_missing = self.df.isna().sum().sum()
        completeness = ((total_cells - total_missing) / total_cells) * 100 if total_cells > 0 else 100

        # оценка: 100 минус штрафы
        penalty = 0
        for issue in self.issues:
            if issue.severity == 'high':
                penalty += 10
            elif issue.severity == 'medium':
                penalty += 5
            else:
                penalty += 2

        quality_score = max(0.0, 100.0 - penalty)

        metrics = {
            "completeness_score": round(completeness, 2),
            "quality_score": round(quality_score, 2),
            "total_errors_found": float(len(self.issues))
        }

        return QualityReport(
            timestamp=datetime.now().isoformat(),
            total_rows=self.total_rows,
            total_columns=len(self.df.columns),
            metrics=metrics,
            issues=self.issues
        )
