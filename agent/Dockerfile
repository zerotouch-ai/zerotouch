FROM python:3.11-slim

WORKDIR /app

# docker CLI so the agent can run subprocess remediation (restart/logs/exec)
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent.py"]
