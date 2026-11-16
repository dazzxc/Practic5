"""Проверка 1: пропуски - пустые ячейки в каждой колонке."""

from checks.issue import make_issue, has_value


def check_missing(df):
    """По одной ошибке на каждую колонку, где есть пустые ячейки."""
    issues = []
    total = len(df)

    for column in df.columns:
        is_empty = ~has_value(df[column])
        bad_rows = df.index[is_empty].tolist()

        if bad_rows:
            issues.append(make_issue(
                issue_type="missing",
                column=column,
                bad_rows=bad_rows,
                total_rows=total,
                message=f"В колонке '{column}' пусто в {len(bad_rows)} строках из {total}",
            ))

    return issues
