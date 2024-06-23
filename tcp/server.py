import socket
import threading
from utils import SERVER_IP, PORT, SIZE, FORMAT, DISCONNECT_MSG

IP = socket.gethostbyname(socket.gethostname())

class TCP_Server:

    def __init__(self):
        print("[STARTING] Server is starting...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()
        print(f"[LISTENING] Server is listening on {SERVER_IP}:{PORT}")

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")    

        connected = True
        while connected:
            msg = conn.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False
            print(f"[{addr}] {msg}")
            msg = f"Msg received: {msg}"
            conn.send(msg.encode(FORMAT))

        conn.close()

    def execute(self):
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn,addr))
            thread.start()       
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    server = TCP_Server()
    server.execute()