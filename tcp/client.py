import socket
from utils import SERVER_IP, PORT, SIZE, FORMAT, DISCONNECT_MSG

IP = socket.gethostbyname(socket.gethostname())

class TCP_Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))
        print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    def execute(self):
        connected = True
        while connected:
            msg = input("> ")

            client.send(msg.encode(FORMAT))

            if(msg == DISCONNECT_MSG):
                connected = False
            else:
                msg.client.recv(SIZE).decode(FORMAT)
                print(f"[SERVER] {msg}")
            

if __name__ == "__main__":
    client = TCP_Client()
    client.execute()

    