import os
import sys
import multiprocessing
import threading
import time
import uvicorn
import webview
import socket

# For PyInstaller: determine if we are running in a bundle
IS_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if IS_BUNDLED:
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_server(port):
    # Ensure the working directory is correct for the backend
    if IS_BUNDLED:
        os.chdir(sys._MEIPASS)
    
    from web.backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    # Required for Windows executables using multiprocessing
    multiprocessing.freeze_support()
    
    # Standard desktop app configuration
    port = 8000
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for the server to be ready
    retries = 15
    while not is_port_open(port) and retries > 0:
        time.sleep(1)
        retries -= 1

    if retries == 0:
        print("Error: Could not start the backend server.")
        sys.exit(1)

    # Launch the webview window
    window = webview.create_window(
        'Discord Terminator',
        f'http://127.0.0.1:{port}',
        width=1200,
        height=850,
        resizable=True,
        min_size=(800, 600),
        zoomable=True  # Enable native zooming
    )

    # Fallback/Enhancement: Add manual keyboard listener for zoom shortcuts
    # This ensures Ctrl+Plus, Ctrl+Minus, and Ctrl+0 work across all engines
    def inject_zoom(window):
        zoom_js = """
        window.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === '=' || e.key === '+') {
                    e.preventDefault();
                    document.body.style.zoom = (parseFloat(document.body.style.zoom || 1) + 0.1);
                } else if (e.key === '-') {
                    e.preventDefault();
                    document.body.style.zoom = (parseFloat(document.body.style.zoom || 1) - 0.1);
                } else if (e.key === '0') {
                    e.preventDefault();
                    document.body.style.zoom = 1.0;
                }
            }
        });
        """
        window.evaluate_js(zoom_js)

    webview.start(inject_zoom, window)
