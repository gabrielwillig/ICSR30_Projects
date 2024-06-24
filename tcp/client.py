import socket
import struct 
import threading
from utils import PORT, BUFFER_SIZE, CHECKSUM_SIZE, PACKET_SIZE, FORMAT, DISCONNECT_MSG, SERVER_IP, calculate_sha_checksum

IP = SERVER_IP#socket.gethostbyname(socket.gethostname())

class ChecksumFailed(Exception):
    pass

class TCP_Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))
        self.last_packet = -1
        self.connected = True
        self.old_checksum = b""
        self.isTransmitting = False
        self.file = None
        self.file_name = None
        self.packets = 0
        print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    def execute(self):
        input_thread = threading.Thread(target=self.read_input)  # Thread para ler entradas do teclado
        input_thread.start()

        while self.connected:
            server_msg = self.receive()
            if(self.isTransmitting):
                self.handle_file(server_msg)
            else:
                server_msg = server_msg.decode(FORMAT)
                print(server_msg)

        self.client.close()

    def handle_file(self, msg: str):
        if(msg.startswith(b"[CHECKSUM]")):
            msg = msg.replace(b"[CHECKSUM]", b"")
            self.old_checksum = msg
            return
        elif(msg.startswith(b"[FOUND]")):
            msg = msg.decode(FORMAT)
            split = msg.split(" ")
            self.last_packet = 0
            print(msg)
            self.packets = int(split[1])
            self.ack_request(self.file_name, self.last_packet+1)
            return
        elif(msg.startswith(b"[ERROR]")):
            msg = msg.decode(FORMAT)
            print(msg)
            self.isTransmitting = False
            return
        else:
            content = msg[PACKET_SIZE:]
            packet_part = struct.unpack(">q", msg[0:PACKET_SIZE])[0]
            if packet_part != (self.last_packet + 1):
                return
            print(f"Receiving package: {packet_part}")
            self.file.write(content)
            self.last_packet += 1
            if(self.last_packet < self.packets):
                try:
                    self.ack_request(self.file_name, self.last_packet+1)
                except TimeoutError:
                    print(f'Timeout error in packet: {self.last_packet+1}')
                except Exception as e:
                    print(f'Error in packet {self.last_packet+1} -> {e}')
            else:
                print(f"Imported file: {self.file_name}")
                self.file.close()
                with open(f"../duplicate/{self.file_name}", 'rb') as f:
                    new_checksum = calculate_sha_checksum(f.read())
                if(new_checksum != self.old_checksum):
                    print("Invalid SHA Checksum!")
                    self.client.send((f"GET {self.file_name}").encode(FORMAT))
                    self.get_request(self.file_name)
                else:
                    print("Valid SHA Checksum!")
                self.isTransmitting = False
            return
        
    def read_input(self):
        while self.connected:
            message = input()
            if(message == DISCONNECT_MSG):
                self.connected = False
            elif("GET" in message):
                split = message.split(' ')    
                file_name = split[1]
                self.get_request(file_name)
            elif("ACK" in message):
                print("[ERROR] You cannot send an ACK!")
            self.client.send(message.encode(FORMAT))

    def get_request(self, file_name):
        self.file = open(f"../duplicate/{file_name}", "wb+")
        self.file_name = file_name
        self.isTransmitting = True

    def ack_request(self, file_name, packet: int):
        msg = (f'ACK {file_name} {packet}').encode(FORMAT)
        self.client.send(msg)

    def receive(self):
        msg = self.client.recv(BUFFER_SIZE)
        return msg
        # if(msg.startswith(b"[CHECKSUM]")):
        #     msg = msg.replace(b"[CHECKSUM]", b"")
        #     self.old_checksum = msg
        #     return msg
        # return msg.decode(FORMAT)

if __name__ == "__main__":
    client = TCP_Client()
    client.execute()