"""
main.py — CipherX entry point
Starts the Flask development server and opens the browser automatically.
"""

import sys
import os
import threading
import webbrowser
import socket

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import app

HOST = "127.0.0.1"
PORT = 5000

def is_port_available(port):
    """Check if a port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((HOST, port))
        sock.close()
        return True
    except OSError:
        return False

# Find an available port
while not is_port_available(PORT):
    PORT += 1

URL  = f"http://{HOST}:{PORT}"

def open_browser():
    """Open the default browser after a short delay."""
    import time
    time.sleep(1.2)
    webbrowser.open(URL)


if __name__ == "__main__":
    print("\n" + "=" * 52)
    print("  CipherX -- Cryptography Suite")
    print("=" * 52)
    print(f"  Local:   {URL}")
    print(f"  Press Ctrl+C to stop the server")
    print("=" * 52 + "\n")

    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
