import os
import time
import json
import redis
import mlflow
from features import build_feature_vector
from model import train_model, load_model, score_vector

REDIS_HOST = "redis"
REDIS_PORT = 6379
POLL_INTERVAL = 5
TRAINING_SAMPLES = 60

mlflow.set_tracking_uri("http://172.17.0.1:5001")
mlflow.set_experiment("zerotouch")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def detect_cause(vector: dict) -> str:
    if vector["memory_rate"] > 5:
        return "memory_leak"
    if vector["cpu_max"] > 85:
        return "cpu_spike"
    if vector["error_rate"] > 10:
        return "high_error_rate"
    if vector["latency_p95"] > 1.0:
        return "high_latency"
    return "unknown"

def publish_anomaly(feature_vector: dict, score: float):
    payload = {
        "anomaly_score": round(abs(score), 4),
        "metrics": feature_vector,
        "probable_cause": detect_cause(feature_vector),
        "timestamp": time.time()
    }
    r.publish("anomalies", json.dumps(payload))
    print(f"Anomaly published to Redis: {payload}")

def collect_baseline() -> list:
    print("Collecting baseline data for training...")
    samples = []
    for i in range(TRAINING_SAMPLES):
        vector = build_feature_vector()
        samples.append(vector)
        print(f"Sample {i+1}/{TRAINING_SAMPLES}: {vector}")
        time.sleep(POLL_INTERVAL)
    return samples

def main():
    print("ZeroTouch ML Worker starting...")
    baseline = collect_baseline()
    model = train_model(baseline)
    print("Model trained. Starting real-time anomaly detection...")

    while True:
        try:
            vector = build_feature_vector()
            is_anomaly, score = score_vector(model, vector)
            if is_anomaly:
                print(f"ANOMALY DETECTED - score: {score}")
                with mlflow.start_run(run_name="anomaly_detected"):
                    mlflow.log_metric("anomaly_score", abs(score))
                    mlflow.log_metrics(vector)
                    mlflow.log_param("cause", detect_cause(vector))
                publish_anomaly(vector, score)
            else:
                print(f"Normal - score: {score:.4f}")
        except Exception as e:
            print(f"Error in worker loop: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
