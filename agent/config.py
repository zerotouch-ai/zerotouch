import os

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "ollama"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_key_here")
GROQ_MODEL = "mistral-saba-24b"

# Offline backup LLM
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-v0.3")

# --- Redis (pub/sub only) ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_CHANNEL = "anomalies"

# --- PostgreSQL (permanent storage + pgvector) ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "zerotouch")
POSTGRES_USER = os.getenv("POSTGRES_USER", "zerotouch")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "zerotouch")

# --- Remediation target ---
TARGET_CONTAINER = os.getenv("TARGET_CONTAINER", "target-app")
