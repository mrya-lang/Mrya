import socket
import threading
import os
import sys

# This will be the bridge between the Python server and the Mrya handler function.
mrya_context = {
    "interpreter": None,
    "handler": None
}

def handle_client(client_socket):
    """Handles a single client connection."""
    global mrya_context
    try:
        request_data = client_socket.recv(1024).decode('utf-8')
        if not request_data:
            return

        # Basic HTTP request parsing
        lines = request_data.split('\r\n')
        if not lines:
            return
        
        try:
            method, path, _ = lines[0].split()
        except ValueError:
            return # Malformed request line

        # Simple security check for allowed IPs if configured
        client_ip = client_socket.getpeername()[0]
        allowed_ips = mrya_context.get("config", {}).get("ALLOWED_IPS")
        if allowed_ips is not None and isinstance(allowed_ips, list) and client_ip not in allowed_ips:
            # Send a 403 Forbidden response
            response = "HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n"
            client_socket.sendall(response.encode('utf-8'))
            return
        interpreter = mrya_context.get("interpreter")
        handler = mrya_context.get("handler")

        if not interpreter or not handler:
            response_body = "Mrya handler not configured."
            status_code = 500
        else:
            # Use the interpreter's calling mechanism
            response_map = interpreter.call_function_or_method(handler, [path, method])
            status_code = int(response_map.get("status", 500)) 
            response_body_raw = response_map.get("body", b"")
        
        # Default content type
        content_type = "text/html; charset=utf-8"
        response_body_bytes = b""
        
        # If the body is raw bytes (from fetch()), it's likely a static file.
        # Determine the content type from the request path.
        if isinstance(response_body_raw, bytes):
            content_type_map = {
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon"
            }
            file_ext = os.path.splitext(path)[1]
            # Default to a generic byte stream if extension is unknown
            content_type = content_type_map.get(file_ext, "application/octet-stream") 
            response_body_bytes = response_body_raw
        else:
            # It's a regular string response, encode it.
            response_body_bytes = str(response_body_raw).encode('utf-8')

        # Construct HTTP response
        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}.get(status_code, "Error")
        response = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(response_body_bytes)}\r\n"
        response += "Connection: close\r\n\r\n"

        client_socket.sendall(response.encode('utf-8') + response_body_bytes)
    finally:
        client_socket.close()

def server_loop(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Mrya server running on http://{host}:{port} ...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def file_watcher(interpreter, watch_dirs):
    """Monitors files for changes and restarts the script."""
    mtimes = {}
    while True:
        for directory in watch_dirs:
            for root, _, files in os.walk(directory):
                for filename in files:
                    # Watch Mrya, HTML, CSS, and JS files
                    if filename.endswith(('.mrya', '.html', '.css', '.js')):
                        path = os.path.join(root, filename)
                        try:
                            mtime = os.stat(path).st_mtime
                            if path not in mtimes:
                                mtimes[path] = mtime
                            elif mtimes[path] < mtime:
                                print(f"\n* Change detected in '{path}'. Restarting server...")
                                # This replaces the current process with a new one
                                os.execv(sys.executable, [sys.executable] + sys.argv)
                        except FileNotFoundError:
                            # File might have been deleted, restart
                            print(f"\n* Deletion detected for '{path}'. Restarting server...")
                            os.execv(sys.executable, [sys.executable] + sys.argv)
        interpreter.native_modules['time'].methods['sleep'](1)

def run_server(interpreter, handler, host, port, config):
    global mrya_context
    mrya_context = {"interpreter": interpreter, "handler": handler, "config": config}
    
    # Run the server loop in a daemon thread
    server_thread = threading.Thread(target=server_loop, args=(host, int(port)))
    server_thread.daemon = True
    server_thread.start()

    # If in debug mode, start the file watcher. Otherwise, just wait.
    if config.get("DEBUG"):
        print("* Debug mode is ON. Watching for file changes...")
        # Watch the current directory (where the script is run) and the packages directory
        watch_dirs = [os.getcwd(), os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "packages"))]
        file_watcher(interpreter, watch_dirs)
    else:
        try:
            while True:
                interpreter.native_modules['time'].methods['sleep'](3600) # Sleep for a long time
        except KeyboardInterrupt:
            print("\nShutting down server.")