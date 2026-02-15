import os
import sys
import multiprocessing
import threading
import time
import uvicorn
import webview
import socket

# Add the project root to sys.path to allow importing the backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_server(port):
    from web.backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    # Standard desktop app configuration
    port = 8000
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for the server to be ready
    retries = 10
    while not is_port_open(port) and retries > 0:
        time.sleep(1)
        retries -= 1

    if retries == 0:
        print("Error: Could not start the backend server.")
        sys.exit(1)

    # Launch the webview window
    webview.create_window(
        'Stoat Migrate - Discord Terminator',
        f'http://127.0.0.1:{port}',
        width=1000,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    
    webview.start()
