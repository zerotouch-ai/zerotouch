from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint']
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Current CPU usage percent'
)

MEMORY_USAGE = Gauge(
    'memory_usage_percent',
    'Current memory usage percent'
)