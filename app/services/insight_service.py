from app.llm.insight_prompts import build_result_explanation_prompt
from app.llm.ollama_client import generate_json_with_ollama


def generate_text_response_and_insights(
    user_prompt: str,
    sql: str,
    result: dict,
    model: str = "llama3:8b"
) -> dict:
    prompt = build_result_explanation_prompt(
        user_prompt=user_prompt,
        sql=sql,
        result=result
    )

    try:
        data = generate_json_with_ollama(prompt, model=model)

        text_response = data.get("text_response", "").strip()
        insights = data.get("insights", [])

        if not isinstance(insights, list):
            insights = []

        return {
            "text_response": text_response,
            "insights": insights[:3]
        }

    except Exception:
        rows = result.get("rows", [])
        row_count = result.get("row_count", 0)

        if row_count == 0:
            return {
                "text_response": "No matching data was found.",
                "insights": []
            }

        return {
            "text_response": f"Found {row_count} matching rows.",
            "insights": ["Structured results are available in the table output."]
        }