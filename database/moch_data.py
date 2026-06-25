import psycopg2
import json
import random
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="zerotouch",
    user="zerotouch",
    password="zerotouch"
)
cur = conn.cursor()

anomaly_types = ["memory_leak", "cpu_spike", "high_error_rate", "high_latency"]
actions = ["restart_container", "get_logs", "clear_cache"]

for i in range(20):
    anomaly_type = random.choice(anomaly_types)
    cur.execute("""
        INSERT INTO incidents
        (timestamp, anomaly_type, anomaly_score, metrics, action_taken, reasoning, resolution_time, resolved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        datetime.now() - timedelta(minutes=random.randint(1, 120)),
        anomaly_type,
        round(random.uniform(0.7, 0.99), 4),
        json.dumps({
            "cpu_mean": random.uniform(20, 95),
            "memory_mean": random.uniform(30, 95),
            "latency_p95": random.uniform(0.05, 3.0),
            "error_rate": random.uniform(0, 50)
        }),
        random.choice(actions),
        f"Detected {anomaly_type}. Retrieved runbook and executed remediation automatically.",
        round(random.uniform(5, 90), 2),
        True
    ))

conn.commit()
cur.close()
conn.close()
print("20 mock incidents inserted.")