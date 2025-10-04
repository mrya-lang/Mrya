import socket
import threading

# This will be the bridge between the Python server and the Mrya handler function.
mrya_context = {
    "interpreter": None,
    "handler": None
}

def handle_client(client_socket):
    """Handles a single client connection."""
    try:
        request_data = client_socket.recv(1024).decode('utf-8')
        if not request_data:
            return

        # Basic HTTP request parsing
        lines = request_data.split('\r\n')
        if not lines:
            return
        
        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            return
            
        method, path = parts[0], parts[1]

        global mrya_context
        interpreter = mrya_context.get("interpreter")
        handler = mrya_context.get("handler")

        if not interpreter or not handler:
            response_body = "Mrya handler not configured."
            status_code = 500
        else:
            # Use the interpreter's calling mechanism
            response_map = interpreter.call_function_or_method(handler, [path, method])
            status_code = response_map.get("status", 500)
            response_body = response_map.get("body", "")

        # Construct HTTP response
        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}.get(status_code, "Error")
        response = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response += "Content-Type: text/html\r\n"
        response += f"Content-Length: {len(response_body)}\r\n"
        response += "Connection: close\r\n\r\n"
        response += str(response_body)

        client_socket.sendall(response.encode('utf-8'))
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

def run_server(interpreter, handler, host, port):
    global mrya_context
    mrya_context = {"interpreter": interpreter, "handler": handler}
    
    # Run the server loop in a daemon thread
    server_thread = threading.Thread(target=server_loop, args=(host, int(port)))
    server_thread.daemon = True
    server_thread.start()

    # Keep the main thread alive to listen for Ctrl+C
    try:
        while True:
            # Use the interpreter's time module to sleep
            interpreter.native_modules['time'].methods['sleep'](1)
    except KeyboardInterrupt:
        print("\nShutting down server.")