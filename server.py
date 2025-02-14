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
