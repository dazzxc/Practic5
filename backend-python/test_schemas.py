from app.schemas.common import Issue
from app.schemas.profile import DataProfile
from app.schemas.report import Report


issue = Issue(
    type="missing_values",
    column="age",
    description="Column contains missing values",
    count=5,
    recommendation="Fill missing values"
)

profile = DataProfile(
    file_name="users.csv",
    file_type="CSV",
    rows_count=100,
    columns_count=3,
    columns=["name", "age", "email"],
    missing_values=5,
    duplicates=2
)

report = Report(
    report_id="report-001",
    status="completed",
    profile=profile,
    issues=[issue],
    total_issues=1,
    recommendations=["Check missing values in age column"]
)

print(report.model_dump())