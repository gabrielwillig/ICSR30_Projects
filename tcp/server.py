import socket
import threading
import math
import struct
from utils import SERVER_IP, PORT, DATA_SIZE, BUFFER_SIZE, FORMAT, DISCONNECT_MSG, calculate_sha_checksum

IP = socket.gethostbyname(socket.gethostname())#SERVER_IP

class TCP_Server:

    def __init__(self):
        print("[STARTING] Server is starting...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()
        print(f"[LISTENING] Server is listening on {IP}:{PORT}")
        self.clients = []  # Lista para armazenar as conexões dos clientes

    def execute(self):
        input_thread = threading.Thread(target=self.read_input)  # Thread para ler entradas do teclado
        input_thread.start()

        while True:
            try:
                conn, addr = self.server.accept()
                self.clients.append(conn)  # Adiciona a nova conexão à lista de clientes
                thread = threading.Thread(target=self.handle_client, args=(conn,addr))
                thread.start()    
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")  # Exclui a thread de input
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break

    def read_input(self):
        while True:
            message = input()  # Lê entrada do teclado
            self.broadcast_to_all(f"[SERVER-MESSAGE] {message}")

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")    

        connected = True
        while connected:
            msg = conn.recv(BUFFER_SIZE).decode(FORMAT)

            print(f"[{addr}] {msg}")

            split = msg.split(' ')

            if(msg == DISCONNECT_MSG):
                connected = False
            elif(len(split) > 1):
                file_name = split[1]
                if(split[0] == "GET"):
                    self.get_request(conn, file_name)
                elif(split[0] == "ACK"):
                    packet = int(split[2])
                    self.ack_request(conn, file_name, packet)
            self.broadcast(f"[SERVER] Received message: {msg}", conn)    
        conn.close()

    def get_request(self, conn, file_name):
        checksum = b"[CHECKSUM]"
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                checksum = checksum + calculate_sha_checksum(content)
                packets = math.ceil(len(content)/DATA_SIZE)
                message = f'[FOUND] {packets} packets!'
        except FileNotFoundError:
            message = f'[ERROR] File: {file_name} not found!'    
        except Exception as e:
            message = f'[ERROR] {e}!'
        finally:
            self.broadcast(checksum, conn)
            self.broadcast(message, conn)

    def ack_request(self, conn, file_name, packet: int):
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                packets = math.ceil(len(content)/DATA_SIZE)
                if packet > packets:
                    message = '[ERROR] exceeded maximum packet number'
                else:
                    start = DATA_SIZE * (packet - 1)
                    end = start + DATA_SIZE
                    response = content[start:end]
                    message = struct.pack(">q", packet) + response
        except FileNotFoundError:
            message = f'[ERROR] File {file_name} not found!'    
        except Exception as e:
            message = f'[ERROR] {e}!'
        finally:
            self.broadcast(message, conn)

    def broadcast(self, msg, conn):
        if type(msg) is str:
           msg = bytes(msg, FORMAT)
        conn.send(msg)

    def broadcast_to_all(self, msg):
        if type(msg) is str:
            msg = bytes(msg, FORMAT)
        for client in self.clients:
            try:
                client.send(msg)
            except Exception as e:
                print(f"[ERROR] sending message to client: {e}")
                self.clients.remove(client)

if __name__ == "__main__":
    server = TCP_Server()
    server.execute()