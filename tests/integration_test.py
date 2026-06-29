import requests
import redis
import psycopg2
import json
import time

RESULTS = []

def check(name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} — {name} {detail}")
    RESULTS.append(passed)

def test_target_app():
    try:
        r = requests.get("http://localhost:8000/", timeout=5)
        check("Target app is running", r.status_code == 200)
        r = requests.get("http://localhost:8000/metrics", timeout=5)
        check("Metrics endpoint exposed", r.status_code in [200, 307])
    except Exception as e:
        check("Target app is running", False, str(e))

def test_prometheus():
    try:
        r = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        data = r.json()
        targets = data["data"]["activeTargets"]
        target_up = any(t["health"] == "up" for t in targets)
        check("Prometheus scraping target app", target_up)
    except Exception as e:
        check("Prometheus running", False, str(e))

def test_redis():
    try:
        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        check("Redis is running", True)
    except Exception as e:
        check("Redis is running", False, str(e))

def test_postgres():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432,
            dbname="zerotouch", user="zerotouch",
            password="zerotouch"
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM incidents;")
        count = cur.fetchone()[0]
        check("PostgreSQL is running", True, f"({count} incidents)")
        cur.close()
        conn.close()
    except Exception as e:
        check("PostgreSQL is running", False, str(e))

def test_mlflow():
    try:
        r = requests.get("http://localhost:5001/health", timeout=5)
        check("MLflow is running", r.status_code == 200)
    except Exception as e:
        check("MLflow is running", False, str(e))

def test_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = r.json().get("models", [])
        mistral_available = any("mistral" in m["name"] for m in models)
        check("Ollama is running", True)
        check("Mistral model available", mistral_available)
    except Exception as e:
        check("Ollama is running", False, str(e))

if __name__ == "__main__":
    print("\n🔍 ZeroTouch Integration Tests\n" + "="*40)
    test_target_app()
    test_prometheus()
    test_redis()
    test_postgres()
    test_mlflow()
    test_ollama()
    print("\n" + "="*40)
    passed = sum(RESULTS)
    total = len(RESULTS)
    print(f"Results: {passed}/{total} passed")
    if passed == total:
        print("✅ System is fully operational. Ready for demo.")
    else:
        print("❌ Some checks failed. Fix before demo day.")
