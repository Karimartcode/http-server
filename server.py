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
