"""
Проверка 1: пропуски.

Ищет пустые ячейки в каждой колонке:
None, NaN и пустые строки ("" или "   ").
"""

from checks.issue import make_issue, has_value


def check_missing(df):
    """Возвращает список проблем: по одной на каждую колонку с пропусками."""
    issues = []
    total = len(df)

    for column in df.columns:
        is_empty = ~has_value(df[column])  # True там, где пусто
        bad_rows = df.index[is_empty].tolist()

        if bad_rows:  # если пропуски есть
            issues.append(make_issue(
                issue_type="missing",
                column=column,
                bad_rows=bad_rows,
                total_rows=total,
                message=f"В колонке '{column}' пусто в {len(bad_rows)} строках из {total}",
            ))

    return issues
