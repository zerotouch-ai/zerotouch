import docker
from config import TARGET_CONTAINER

client = docker.from_env()

def restart_container() -> str:
    print(f"TOOL: Restarting {TARGET_CONTAINER}...")
    try:
        container = client.containers.get(TARGET_CONTAINER)
        container.restart()
        return f"Container {TARGET_CONTAINER} restarted successfully."
    except Exception as e:
        return f"Restart error: {str(e)}"

def get_logs() -> str:
    print(f"TOOL: Fetching logs from {TARGET_CONTAINER}...")
    try:
        container = client.containers.get(TARGET_CONTAINER)
        return container.logs(tail=50).decode("utf-8")
    except Exception as e:
        return f"Log fetch error: {str(e)}"

def clear_cache() -> str:
    print("TOOL: Clearing cache...")
    try:
        container = client.containers.get(TARGET_CONTAINER)
        result = container.exec_run("python -c 'import gc; gc.collect(); print(\"Cache cleared\")'")
        return result.output.decode("utf-8")
    except Exception as e:
        return f"Cache clear error: {str(e)}"

TOOLS = {
    "restart_container": restart_container,
    "get_logs": get_logs,
    "clear_cache": clear_cache
}
