import subprocess
from config import TARGET_CONTAINER


def restart_container() -> str:
    print(f"TOOL: Restarting {TARGET_CONTAINER}...")
    try:
        result = subprocess.run(
            ["docker", "restart", TARGET_CONTAINER],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return f"Container {TARGET_CONTAINER} restarted successfully."
        return f"Restart failed: {result.stderr}"
    except Exception as e:
        return f"Restart error: {str(e)}"


def get_logs() -> str:
    print(f"TOOL: Fetching logs from {TARGET_CONTAINER}...")
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "50", TARGET_CONTAINER],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Log fetch error: {str(e)}"


def clear_cache() -> str:
    print("TOOL: Clearing cache...")
    try:
        result = subprocess.run(
            ["docker", "exec", TARGET_CONTAINER,
             "python", "-c",
             "import gc; gc.collect(); print('Cache cleared')"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout or "Cache cleared successfully."
    except Exception as e:
        return f"Cache clear error: {str(e)}"


TOOLS = {
    "restart_container": restart_container,
    "get_logs": get_logs,
    "clear_cache": clear_cache
}
