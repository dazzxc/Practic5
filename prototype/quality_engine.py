import pandas as pd
from datetime import datetime
from .schemas import Issue, QualityReport
from typing import List

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

    def run_all(self) -> QualityReport:
        self.check_missing()
        self.check_duplicates()

        total_cells = self.total_rows * len(self.df.columns)
        total_missing = self.df.isna().sum().sum()
        completeness = ((total_cells - total_missing) / total_cells) * 100 if total_cells > 0 else 100

        metrics = {
            "completeness_score": round(completeness, 2),
            "quality_score": round(max(0.0, 100.0 - (len(self.issues) * 15)), 2),
            "total_errors_found": float(len(self.issues))
        }

        return QualityReport(
            timestamp=datetime.now().isoformat(),
            total_rows=self.total_rows,
            total_columns=len(self.df.columns),
            metrics=metrics,
            issues=self.issues
        )