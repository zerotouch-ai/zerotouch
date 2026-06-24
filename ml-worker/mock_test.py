import random
from model import train_model, score_vector

# Generate fake normal data
def fake_normal():
    return {
        "cpu_mean": random.uniform(20, 40),
        "cpu_max": random.uniform(30, 50),
        "cpu_rate": random.uniform(0, 1),
        "memory_mean": random.uniform(30, 50),
        "memory_max": random.uniform(40, 60),
        "memory_rate": random.uniform(0, 1),
        "latency_mean": random.uniform(0.05, 0.15),
        "latency_p95": random.uniform(0.1, 0.3),
        "error_rate": random.uniform(0, 1),
    }

# Generate fake anomaly data
def fake_anomaly():
    return {
        "cpu_mean": random.uniform(85, 100),
        "cpu_max": 100,
        "cpu_rate": random.uniform(5, 10),
        "memory_mean": random.uniform(80, 95),
        "memory_max": 95,
        "memory_rate": random.uniform(8, 15),
        "latency_mean": random.uniform(1.5, 3.0),
        "latency_p95": random.uniform(2.0, 5.0),
        "error_rate": random.uniform(20, 50),
    }

# Train on normal data
print("Training on normal data...")
training_data = [fake_normal() for _ in range(60)]
model = train_model(training_data)

# Test on normal
print("\nTesting normal samples:")
for _ in range(3):
    v = fake_normal()
    is_anomaly, score = score_vector(model, v)
    print(f"  is_anomaly={is_anomaly}, score={score:.4f}")

# Test on anomaly
print("\nTesting anomaly samples:")
for _ in range(3):
    v = fake_anomaly()
    is_anomaly, score = score_vector(model, v)
    print(f"  is_anomaly={is_anomaly}, score={score:.4f}")
