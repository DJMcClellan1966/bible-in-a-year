#!/usr/bin/env python3
"""
Windows desktop wrapper using pywebview.
"""

import atexit
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
import webview


def start_backend() -> subprocess.Popen:
    project_root = Path(__file__).parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "backend.log"
    log_file = open(log_path, "w", encoding="utf-8")

    return subprocess.Popen(
        [sys.executable, "-m", "backend.main"],
        cwd=str(project_root),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def wait_for_backend(url: str, timeout_seconds: int = 60) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException:
            time.sleep(0.5)
    raise RuntimeError("Backend server did not start in time. Check logs/backend.log.")


def main() -> None:
    backend = start_backend()

    def cleanup() -> None:
        if backend and backend.poll() is None:
            backend.terminate()
            backend.wait(timeout=5)

    atexit.register(cleanup)

    base_url = "http://127.0.0.1:8000"
    wait_for_backend(f"{base_url}/api/health")

    webview.create_window(
        "Bible in a Year",
        f"{base_url}/static/index.html",
        width=1200,
        height=800,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
