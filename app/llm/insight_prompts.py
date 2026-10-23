import json


def build_result_explanation_prompt(user_prompt: str, sql: str, result: dict) -> str:
    sample_rows = result.get("rows", [])[:10]

    payload = {
        "user_prompt": user_prompt,
        "sql": sql,
        "columns": result.get("columns", []),
        "rows": sample_rows,
        "row_count": result.get("row_count", 0),
    }

    return f"""
You are a data analyst assistant.

A user asked a question and a SQL query was executed successfully.

Your job:
1. Write a direct plain-English answer to the user
2. Give 2 or 3 short insights
3. Be concise
4. Do not mention SQL unless necessary
5. If there are no rows, clearly say no matching data was found

Return valid JSON only in this exact format:
{{
  "text_response": "short answer",
  "insights": ["insight 1", "insight 2", "insight 3"]
}}

Data:
{json.dumps(payload, indent=2)}
""".strip()