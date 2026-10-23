from sqlalchemy import text
import sqlglot
from sqlglot import expressions as exp
import re


BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "CREATE", "REPLACE", "ATTACH", "DETACH",
    "PRAGMA", "VACUUM"
}


def normalize_sql_output(sql: str) -> str:
    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "").strip()

    if sql.upper().startswith("SQL:"):
        sql = sql[4:].strip()

    # Fix common LLM mistake:
    # ... ); LIMIT 10;
    # ... ); ORDER BY ...
    # ... ); GROUP BY ...
    sql = re.sub(r";\s+(LIMIT|ORDER BY|GROUP BY|HAVING)\b", r" \1", sql, flags=re.IGNORECASE)

    # remove repeated semicolons and keep only one trailing semicolon
    sql = re.sub(r";{2,}", ";", sql).strip()

    return sql


def is_safe_select_sql(sql: str) -> tuple[bool, str]:
    cleaned = normalize_sql_output(sql)
    upper = cleaned.upper()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in upper:
            return False, f"Blocked keyword detected: {keyword}"

    # allow one optional trailing semicolon, but block true multi-statement SQL
    without_trailing = cleaned[:-1] if cleaned.endswith(";") else cleaned
    if ";" in without_trailing:
        return False, "Multiple SQL statements are not allowed"

    try:
        parsed = sqlglot.parse_one(cleaned)
    except Exception as e:
        return False, f"Invalid SQL: {str(e)}"

    if not isinstance(parsed, exp.Select):
        return False, "Only SELECT queries are allowed"

    return True, "SQL is safe"


def run_select_query(engine, sql: str):
    cleaned = normalize_sql_output(sql)

    with engine.connect() as conn:
        result = conn.execute(text(cleaned))
        columns = list(result.keys()) if result.returns_rows else []
        rows = [dict(row._mapping) for row in result] if result.returns_rows else []

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }