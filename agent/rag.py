import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

model = SentenceTransformer('all-MiniLM-L6-v2')

RUNBOOKS = [
    {
        "title": "memory_leak",
        "content": "High memory usage detected. Memory is growing continuously indicating a leak. Action: restart the container immediately to free memory. Then monitor if memory stabilizes below 60%."
    },
    {
        "title": "cpu_spike",
        "content": "CPU usage is critically high above 85%. This indicates an infinite loop or heavy computation. Action: restart the container to kill the runaway process. Check logs after restart."
    },
    {
        "title": "high_error_rate",
        "content": "HTTP 500 error rate is elevated above 10%. This indicates application errors. Action: fetch the container logs first to identify the root cause, then restart if errors persist."
    },
    {
        "title": "high_latency",
        "content": "Request latency p95 is above 1 second. This indicates slow responses. Action: clear the cache first. If latency remains high after 30 seconds, restart the container."
    }
]


def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


def setup_runbooks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runbooks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            content TEXT,
            embedding vector(384)
        );
    """)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM runbooks;")
    count = cur.fetchone()[0]
    if count == 0:
        print("Inserting runbooks into pgvector...")
        for rb in RUNBOOKS:
            embedding = model.encode(rb["content"]).tolist()
            cur.execute(
                "INSERT INTO runbooks (title, content, embedding) VALUES (%s, %s, %s)",
                (rb["title"], rb["content"], embedding)
            )
        conn.commit()
        print("Runbooks inserted successfully.")
    else:
        print(f"Runbooks already present ({count} rows). Skipping insert.")
    cur.close()
    conn.close()


def get_runbook(anomaly: dict) -> dict:
    """Cosine-similarity search for the closest runbook.

    Returns {"title": ..., "content": ...}. The agent uses both: title is
    persisted as runbook_used, content is fed to the LLM as context.
    """
    query_text = f"{anomaly.get('probable_cause', '')} {str(anomaly.get('metrics', ''))}"
    query_embedding = model.encode(query_text).tolist()
    conn = get_connection()
    cur = conn.cursor()
    # 1 - cosine distance, cast embedding to pgvector type
    cur.execute("""
        SELECT title, content
        FROM runbooks
        ORDER BY embedding <=> %s::vector
        LIMIT 1;
    """, (query_embedding,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        print(f"RAG retrieved runbook: {result[0]}")
        return {"title": result[0], "content": result[1]}
    return {
        "title": "default",
        "content": "No relevant runbook found. Restart the container as default action."
    }
