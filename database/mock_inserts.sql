INSERT INTO incidents (anomaly_type, anomaly_score, metrics, action_taken, reasoning, resolution_time, resolved)
VALUES
('memory_leak', 0.94, '{"cpu": 45, "memory": 88}', 'restart_container', 'Memory growing rapidly. Restarted container.', 12.5, TRUE),
('cpu_spike', 0.87, '{"cpu": 98, "memory": 50}', 'restart_container', 'CPU pinned at 100%. Restarted container.', 8.3, TRUE),
('high_error_rate', 0.91, '{"error_rate": 45}', 'get_logs', 'High 500 errors detected. Fetched logs.', 5.1, TRUE);