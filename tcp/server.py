import socket
import threading
import math
import struct
from utils import SERVER_IP, PORT, DATA_SIZE, BUFFER_SIZE, CHECKSUM_SIZE, PACKET_SIZE, FORMAT, DISCONNECT_MSG, calculate_sha_checksum

IP = SERVER_IP#socket.gethostbyname(socket.gethostname())

class TCP_Server:

    def __init__(self):
        print("[STARTING] Server is starting...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()
        print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    def execute(self):
        while True:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn,addr))
                thread.start()       
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")    

        connected = True
        while connected:
            msg = conn.recv(BUFFER_SIZE).decode(FORMAT)

            print(f"[{addr}] {msg}")

            message = f"Message received: {msg}"
            self.broadcast(message, conn)

            if msg == DISCONNECT_MSG:
                connected = False
                break

            split = msg.split(' ')

            if(len(split) > 1):
                file_name = split[1]
                if(split[0] == "GET"):
                    self.get_request(conn, file_name)
                elif(split[0] == "ACK"):
                    packet = int(split[2])
                    self.ack_request(conn, file_name, packet)

        conn.close()

    def get_request(self, conn, file_name):
        checksum = bytes(" ", 'utf-8')
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                checksum = calculate_sha_checksum(content)
                packets = math.ceil(len(content)/DATA_SIZE)
                message = f'FOUND {packets} packets!'
        except FileNotFoundError:
            message = f'ERROR File: {file_name} not found!'    
        except Exception as e:
            message = f'ERROR {e}!'
        finally:
            self.broadcast(checksum, conn)
            self.broadcast(message, conn)

    def ack_request(self, conn, file_name, packet: int):
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                packets = math.ceil(len(content)/DATA_SIZE)
                if packet > packets:
                    message = 'ERROR exceeded maximum packet number'
                else:
                    start = DATA_SIZE * (packet - 1)
                    end = start + DATA_SIZE
                    response = content[start:end]
                    message = struct.pack(">q", packet) + response
        except FileNotFoundError:
            message = f'ERROR File {file_name} not found!'    
        except Exception as e:
            message = f'ERROR {e}!'
        finally:
            self.broadcast(message, conn)

    def broadcast(self, msg, conn):
        if type(msg) is str:
           msg = bytes(msg, 'utf-8')
        conn.send(msg)

if __name__ == "__main__":
    server = TCP_Server()
    server.execute()