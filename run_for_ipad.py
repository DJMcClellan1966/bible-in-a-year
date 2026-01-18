#!/usr/bin/env python3
"""
Run the Bible in a Year app for iPad/network access.
Starts the backend server accessible from other devices on your network.
"""

import socket
import subprocess
import sys
from pathlib import Path


def get_local_ip() -> str:
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main() -> None:
    """Start the backend server accessible from network."""
    project_root = Path(__file__).parent
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("Bible in a Year - Network Server")
    print("=" * 60)
    print(f"\n📍 Server starting on all network interfaces...")
    print(f"📱 Local IP Address: {local_ip}")
    print(f"\n🌐 Access from iPad:")
    print(f"   http://{local_ip}:8000/static/index.html")
    print(f"\n💻 Access from this computer:")
    print(f"   http://127.0.0.1:8000/static/index.html")
    print("\n" + "=" * 60)
    print("⚠️  Make sure your iPad and computer are on the same Wi-Fi network!")
    print("⚠️  You may need to allow the connection in Windows Firewall")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start uvicorn with 0.0.0.0 to accept connections from all interfaces
    try:
        subprocess.run(
            [
                sys.executable, "-m", "uvicorn",
                "backend.main:app",
                "--host", "0.0.0.0",  # Accept connections from all interfaces
                "--port", "8000",
                "--log-level", "info",
            ],
            cwd=str(project_root),
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")


if __name__ == "__main__":
    main()
