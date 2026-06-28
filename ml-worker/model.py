import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle
import os

MODEL_PATH = "model.pkl"

def train_model(training_data: list):
    df = pd.DataFrame(training_data)
    X = df.values

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Model trained on {len(X)} samples and saved.")
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def score_vector(model, feature_vector: dict) -> tuple:
    X = np.array(list(feature_vector.values())).reshape(1, -1)
    score = model.decision_function(X)[0]
    prediction = model.predict(X)[0]
    is_anomaly = prediction == -1
    print(f"Score: {score:.4f} | Anomaly: {is_anomaly}")
    return is_anomaly, score
