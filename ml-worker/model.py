import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
import pickle
import os

MODEL_PATH = "model.pkl"
ANOMALY_THRESHOLD = 0.0

def train_model(training_data: list[dict]):
    df = pd.DataFrame(training_data)
    X = df.values

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    with mlflow.start_run(run_name="isolation_forest_training"):
        model.fit(X)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("contamination", 0.05)
        mlflow.log_param("training_samples", len(X))
        mlflow.sklearn.log_model(model, "isolation_forest")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Model trained on {len(X)} samples and saved.")
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def score_vector(model, feature_vector: dict) -> tuple[bool, float]:
    X = np.array(list(feature_vector.values())).reshape(1, -1)
    score = model.decision_function(X)[0]
    prediction = model.predict(X)[0]
    is_anomaly = prediction == -1

    with mlflow.start_run(run_name="anomaly_scoring"):
        mlflow.log_metrics(feature_vector)
        mlflow.log_metric("anomaly_score", score)
        mlflow.log_metric("is_anomaly", int(is_anomaly))

    return is_anomaly, score
