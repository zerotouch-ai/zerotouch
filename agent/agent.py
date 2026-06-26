import json
import time

import redis
import psycopg2
import requests
from groq import Groq

from config import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_URL, OLLAMA_MODEL,
    REDIS_HOST, REDIS_PORT, REDIS_CHANNEL,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
)
from tools import TOOLS
from rag import setup_runbooks, get_runbook

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
groq_client = Groq(api_key=GROQ_API_KEY)

VALID_ACTIONS = set(TOOLS.keys())


def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT,
        dbname=POSTGRES_DB, user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


def save_incident(anomaly: dict, runbook_title: str, action: str,
                  reasoning: str, resolution_time: float):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incidents
        (anomaly_type, anomaly_score, metrics, runbook_used,
         action_taken, reasoning, resolution_time, resolved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        anomaly.get("probable_cause", "unknown"),
        anomaly.get("anomaly_score", 0),
        json.dumps(anomaly.get("metrics", {})),
        runbook_title,
        action,
        reasoning,
        resolution_time,
        True,
    ))
    conn.commit()
    cur.close()
    conn.close()
    print("Incident saved to PostgreSQL.")


def build_prompt(anomaly: dict, runbook: str) -> str:
    return f"""You are an AIOps agent managing containerized infrastructure.

Anomaly detected:
{json.dumps(anomaly, indent=2)}

Relevant runbook:
{runbook}

Available tools:
- restart_container: restarts the target application container
- get_logs: fetches the last 50 lines of container logs
- clear_cache: clears application cache

Based on the anomaly and runbook, decide which single tool to call.
Respond with ONLY the tool name. Nothing else.
Options: restart_container, get_logs, clear_cache"""


def _call_groq(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()


def _call_ollama(prompt: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def call_llm(anomaly: dict, runbook: str) -> str:
    """Decide the remediation tool. Groq primary, Ollama offline backup."""
    prompt = build_prompt(anomaly, runbook)

    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt)

    try:
        return _call_groq(prompt)
    except Exception as e:
        print(f"Groq call failed ({e}); falling back to Ollama...")
        try:
            return _call_ollama(prompt)
        except Exception as e2:
            print(f"Ollama fallback failed ({e2}); defaulting to restart.")
            return "restart_container"


def normalize_action(raw: str) -> str:
    """Map a loose LLM response onto a known tool name."""
    text = (raw or "").lower()
    for name in VALID_ACTIONS:
        if name in text:
            return name
    return "restart_container"


def handle_anomaly(anomaly: dict):
    print(f"\n{'='*50}")
    print(f"ANOMALY RECEIVED: {anomaly.get('probable_cause')}")
    print(f"Score: {anomaly.get('anomaly_score')}")
    start_time = time.time()

    runbook = get_runbook(anomaly)
    raw = call_llm(anomaly, runbook["content"])
    action = normalize_action(raw)
    print(f"LLM raw response: {raw!r} -> action: {action}")

    result = TOOLS[action]()
    print(f"Tool result: {result}")

    reasoning = (
        f"Runbook '{runbook['title']}' matched. LLM chose '{action}'. "
        f"Tool output: {result}"
    )
    resolution_time = time.time() - start_time
    save_incident(anomaly, runbook["title"], action, reasoning, resolution_time)
    print(f"Resolved in {resolution_time:.2f} seconds.")
    print(f"{'='*50}\n")


def main():
    print("ZeroTouch AI Agent starting...")
    setup_runbooks()
    pubsub = r.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)
    print(f"Listening on Redis channel: {REDIS_CHANNEL}")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                anomaly = json.loads(message["data"])
                handle_anomaly(anomaly)
            except Exception as e:
                print(f"Error handling anomaly: {e}")


if __name__ == "__main__":
    main()
