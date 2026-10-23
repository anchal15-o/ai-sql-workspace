import httpx
import json


OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_sql_with_ollama(prompt: str, model: str = "llama3:8b") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()


def generate_json_with_ollama(prompt: str, model: str = "llama3:8b") -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
    response.raise_for_status()

    data = response.json()
    raw = data.get("response", "").strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)