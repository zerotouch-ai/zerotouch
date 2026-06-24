import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://prometheus:9090"

def fetch_metric(query: str, minutes: int = 2) -> pd.Series:
    end = datetime.utcnow()
    start = end - timedelta(minutes=minutes)
    
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
        "query": query,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": "2s"
    })
    
    data = response.json()["data"]["result"]
    if not data:
        return pd.Series(dtype=float)
    
    values = data[0]["values"]
    series = pd.Series(
        [float(v[1]) for v in values],
        index=[datetime.fromtimestamp(float(v[0])) for v in values]
    )
    return series

def build_feature_vector() -> dict:
    cpu = fetch_metric("cpu_usage_percent")
    memory = fetch_metric("memory_usage_percent")
    latency = fetch_metric("http_request_duration_seconds_sum")
    errors = fetch_metric('http_requests_total{status_code="500"}')

    def safe_stats(series):
        if series.empty:
            return {"mean": 0, "max": 0, "rate": 0, "p95": 0}
        return {
            "mean": series.mean(),
            "max": series.max(),
            "rate": series.diff().mean(),
            "p95": series.quantile(0.95)
        }

    cpu_stats = safe_stats(cpu)
    mem_stats = safe_stats(memory)
    lat_stats = safe_stats(latency)
    err_stats = safe_stats(errors)

    return {
        "cpu_mean": cpu_stats["mean"],
        "cpu_max": cpu_stats["max"],
        "cpu_rate": cpu_stats["rate"],
        "memory_mean": mem_stats["mean"],
        "memory_max": mem_stats["max"],
        "memory_rate": mem_stats["rate"],
        "latency_mean": lat_stats["mean"],
        "latency_p95": lat_stats["p95"],
        "error_rate": err_stats["mean"],
    }
