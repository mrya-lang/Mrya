import socket
import threading
import os
import sys
import urllib.parse

# This will be the bridge between the Python server and the Mrya handler function.
mrya_context = {
    "interpreter": None,
    "handler": None
}

def handle_client(client_socket):
    """Handles a single client connection."""
    global mrya_context
    try:
        request_data = b""
        # Read until the end of headers (empty line)
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            request_data += chunk
            if b"\r\n\r\n" in request_data:
                break
        if not request_data:
            return

        # Decode request data
        request_text = request_data.decode('utf-8', errors='replace')

        # Basic HTTP request parsing
        lines = request_text.split('\r\n')
        if not lines:
            return
        
        try:
            method, full_path, _ = lines[0].split()
        except ValueError:
            return # Malformed request line

        # Parse path and query string
        parsed_url = urllib.parse.urlparse(full_path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Parse headers
        headers = {}
        i = 1
        while i < len(lines) and lines[i] != "":
            if ": " in lines[i]:
                key, value = lines[i].split(": ", 1)
                headers[key.lower()] = value
            i += 1

        # Read body if POST or PUT
        body = b""
        content_length = int(headers.get("content-length", "0"))
        if content_length > 0:
            remaining = content_length - len(request_data.split(b"\r\n\r\n",1)[1])
            while remaining > 0:
                chunk = client_socket.recv(min(1024, remaining))
                if not chunk:
                    break
                body += chunk
                remaining -= len(chunk)
            body = request_data.split(b"\r\n\r\n",1)[1] + body
        else:
            body = request_data.split(b"\r\n\r\n",1)[1] if b"\r\n\r\n" in request_data else b""

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
            # Build request map for Mrya handler
            request_map = {
                "method": method,
                "path": path,
                "query": {k: v[0] if len(v)==1 else v for k,v in query.items()},
                "headers": headers,
                "body": body.decode('utf-8', errors='replace'),
                "form": {},
                "params": {}
            }
            # Parse form data if POST and content-type is urlencoded
            if method.upper() == "POST":
                content_type = headers.get("content-type", "")
                if "application/x-www-form-urlencoded" in content_type:
                    form_data = urllib.parse.parse_qs(request_map["body"])
                    request_map["form"] = {k: v[0] if len(v)==1 else v for k,v in form_data.items()}

            # Call the Mrya handler with the request map
            response_map = interpreter.call_function_or_method(handler, [request_map])
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