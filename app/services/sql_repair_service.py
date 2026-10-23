from app.db.runner import normalize_sql_output
from app.llm.ollama_client import generate_sql_with_ollama


def repair_sql_with_llm(
    user_prompt: str,
    bad_sql: str,
    validation_message: str,
    model: str = "llama3:8b"
) -> str:
    repair_prompt = f"""
You generated invalid SQLite SQL.

User request:
{user_prompt}

Invalid SQL:
{bad_sql}

Validation error:
{validation_message}

Fix the SQL.

Rules:
- Return exactly one valid SQLite SELECT query
- Output only SQL
- No explanation
- No markdown
- Do not split LIMIT into a separate statement
- Use only one final statement
""".strip()

    fixed_sql = generate_sql_with_ollama(repair_prompt, model=model)
    return normalize_sql_output(fixed_sql)