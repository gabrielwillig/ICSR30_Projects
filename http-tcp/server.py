import socket
import threading
import os

PORT = 9090
FORMAT = 'utf-8'
SIZE = 1024
IP = socket.gethostbyname(socket.gethostname())

class HTTP_TCP_Server:

    def __init__(self):
        print("[STARTING] Server is starting...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()
        self.clients = []  # Inicializa a lista de clientes
        print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    def execute(self):
        try:
            while True:
                client_socket, addr = self.server.accept()
                self.clients.append(client_socket)  # Adiciona a nova conexão à lista de clientes
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()    
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")  # Conta as threads ativas
        except KeyboardInterrupt:
            print("\n[SHUTTING DOWN] Server is shutting down...")
            self.shutdown_server()

    def shutdown_server(self):
        for client in self.clients:
            client.close()
        self.server.close()
        print("[SHUTDOWN] Server has been shut down.")

    def handle_client(self, client_socket, addr):
        print(f"[NEW CONNECTION] {addr} connected.")   

        request = client_socket.recv(SIZE).decode('utf-8')
        print(f'Received request: {request}')

        # Parse da requisição HTTP
        lines = request.split('\n')
        if len(lines) > 0:
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) == 3:
                method, path, version = parts
                if method == 'GET':
                    self.handle_get(client_socket, path)
                else:
                    self.send_response(client_socket, '405 Method Not Allowed', 'text/plain', '[ERROR] 405 - Method Not Allowed')
            else:
                self.send_response(client_socket, '400 Bad Request', 'text/plain', '[ERROR] 400 - Bad Request')
        else:
            self.send_response(client_socket, '400 Bad Request', 'text/plain', '[ERROR] 400 - Bad Request')

        client_socket.close()

    # Função para tratar requisições GET
    def handle_get(self, client_socket, path):
        if path == '/':
            path = '../assets/index.html'

        file_path = '../assets/' + path
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
                content_type = self.get_content_type(file_path)
                self.send_response(client_socket, '200 OK', content_type, content)
        else:
            self.send_response(client_socket, '404 Not Found', 'text/plain', '[ERROR] 404 - Not Found')

    # Função para enviar a resposta HTTP
    def send_response(self, client_socket, status, content_type, content):
        if isinstance(content, str):
            content = content.encode('utf-8')
        response = f'HTTP/1.1 {status}\r\n'
        response += f'Content-Type: {content_type}\r\n'
        response += f'Content-Length: {len(content)}\r\n'
        response += '\r\n'
        client_socket.sendall(response.encode('utf-8') + content)

    def get_content_type(self, file_path):
        if file_path.endswith('.html'):
            return 'text/html'
        elif file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.jpeg') or file_path.endswith('.jpg'):
            return 'image/jpeg'
        else:
            return 'application/octet-stream'

if __name__ == "__main__":
    server = HTTP_TCP_Server()
    server.execute()