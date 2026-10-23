from app.db.introspection import get_schema_info
from app.llm.prompts import build_sql_prompt
from app.llm.ollama_client import generate_sql_with_ollama
from app.services.manual_fallbacks import get_manual_sql_fallback


def generate_sql_from_prompt(engine, user_prompt: str, model: str = "llama3:8b") -> tuple[str, list[dict], str]:
    schema = get_schema_info(engine)

    llm_prompt = build_sql_prompt(
        user_prompt=user_prompt,
        schema_info=schema,
        dialect="sqlite"
    )

    try:
        sql = generate_sql_with_ollama(llm_prompt, model=model)

        if sql and sql.strip():
            return sql, schema, "llm"

    except Exception:
        pass

    fallback_sql = get_manual_sql_fallback(user_prompt)
    if fallback_sql:
        return fallback_sql, schema, "manual_fallback"

    return "", schema, "none"