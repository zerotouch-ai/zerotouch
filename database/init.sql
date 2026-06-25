CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS  incidents
 (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    anomaly_type VARCHAR(100),
    anomaly_score FLOAT,
    metrics JSONB,
    runbook_used TEXT,
    action_taken VARCHAR(100),
    reasoning TEXT,
    resolution_time FLOAT,
    resolved BOOLEAN DEFAULT TRUE
);


CREATE TABLE IF NOT EXISTS runbooks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    content TEXT,
    embedding vector(384)
);