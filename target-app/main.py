import time
import threading
import psutil
from fastapi import FastAPI, Request, Response, status
from prometheus_client import make_asgi_app
from metrics import REQUEST_COUNT, REQUEST_LATENCY, CPU_USAGE, MEMORY_USAGE

app = FastAPI(title="ZeroTouch - Target App")

# Global variables to control chaos states
chaos_threads_running = False
memory_leak_list = []
return_global_error = False

# Background worker for CPU chaos
def cpu_chaos_worker():
    while chaos_threads_running:
        # Infinite math loop to pin a CPU core
        _ = 12345 * 67890

# Background worker for Memory chaos
def memory_chaos_worker():
    global memory_leak_list
    while chaos_threads_running:
        # Append ~10MB of data (10 million characters)
        memory_leak_list.append("X" * 10_000_000)
        time.sleep(0.1)

# Middleware to update metrics and track execution time for EVERY request
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    endpoint = request.url.path
    
    # Skip tracking requests to the /metrics endpoint itself to avoid noise
    if endpoint == "/metrics":
        return await call_next(request)
        
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as e:
        status_code = "500"
        raise e
    finally:
        # Calculate latency
        latency = time.time() - start_time
        
        # Record Prometheus Metrics
        REQUEST_COUNT.labels(endpoint=endpoint, status_code=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        
        # Update system metrics using psutil
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        
    return response

# --- Normal Endpoints ---

@app.get("/")
async def root():
    return {"status": "healthy"}

@app.get("/process")
async def process():
    if return_global_error:
        return Response(
            content='{"error": "Internal Server Error triggered by chaos"}', 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json"
        )
    time.sleep(0.1)
    return {"status": "processed"}

# --- Chaos Endpoints ---

@app.get("/fault/cpu")
async def trigger_cpu_fault():
    global chaos_threads_running
    if not chaos_threads_running:
        chaos_threads_running = True
        # Using native threading to ensure the thread runs independently from the main async loop
        t = threading.Thread(target=cpu_chaos_worker, daemon=True)
        t.start()
    return {"message": "CPU fault injected successfully"}

@app.get("/fault/memory")
async def trigger_memory_fault():
    global chaos_threads_running
    if not chaos_threads_running:
        chaos_threads_running = True
        t = threading.Thread(target=memory_chaos_worker, daemon=True)
        t.start()
    return {"message": "Memory leak fault injected successfully"}

@app.get("/fault/error")
async def trigger_error_fault():
    global return_global_error
    return_global_error = True
    return {"message": "Global HTTP 500 fault injected successfully"}

@app.get("/fault/reset")
async def reset_faults():
    global chaos_threads_running, memory_leak_list, return_global_error
    
    # Stop background loops
    chaos_threads_running = False
    # Turn off error flag
    return_global_error = False
    # Free up memory list allocation
    memory_leak_list.clear()
    
    return {"message": "All faults reset to normal"}

# Mount Prometheus ASGI app to expose /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)