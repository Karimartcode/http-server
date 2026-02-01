import socket


def create_server(host='localhost', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    return server


def receive_request(client_socket):
    data = b''
    while True:
        chunk = client_socket.recv(4096)
        data += chunk
        if len(chunk) < 4096:
            break
    return data.decode('utf-8')


def parse_request(raw):
    lines = raw.split('\r\n')
    if not lines:
        return None
    method, path, version = lines[0].split(' ', 2)
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, val = line.split(':', 1)
            headers[key.strip()] = val.strip()
        elif line == '':
            break
    body_start = raw.find('\r\n\r\n')
    body = raw[body_start + 4:] if body_start >= 0 else ''
    return {"method": method, "path": path, "version": version, "headers": headers, "body": body}


CONTENT_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".txt": "text/plain",
}

def get_content_type(path):
    for ext, ct in CONTENT_TYPES.items():
        if path.endswith(ext):
            return ct
    return "application/octet-stream"


def build_response(status_code, status_text, headers, body):
    response = f"HTTP/1.1 {status_code} {status_text}\r\n"
    for key, val in headers.items():
        response += f"{key}: {val}\r\n"
    response += "\r\n"
    if isinstance(body, bytes):
        return response.encode('utf-8') + body
    return (response + body).encode('utf-8')


import os

STATIC_DIR = "static"

def serve_file(path):
    filepath = os.path.join(STATIC_DIR, path.lstrip('/'))
    if not os.path.isfile(filepath):
        return build_response(404, "Not Found", {"Content-Type": "text/html"}, "<h1>404 Not Found</h1>")
    ct = get_content_type(filepath)
    mode = 'rb' if ct.startswith('image') else 'r'
    with open(filepath, mode) as f:
        content = f.read()
    if isinstance(content, str):
        content = content.encode('utf-8')
    headers = {"Content-Type": ct, "Content-Length": str(len(content))}
    return build_response(200, "OK", headers, content)


routes = {}

def route(path):
    def decorator(fn):
        routes[path] = fn
        return fn
    return decorator

def handle_request(request):
    if not request:
        return build_response(400, "Bad Request", {}, "")
    path = request["path"]
    if path in routes:
        return routes[path](request)
    return serve_file(path)
