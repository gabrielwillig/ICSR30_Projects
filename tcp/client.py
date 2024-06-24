import socket
import struct 
from utils import PORT, BUFFER_SIZE, CHECKSUM_SIZE, PACKET_SIZE, FORMAT, DISCONNECT_MSG, SERVER_IP, calculate_sha_checksum

IP = SERVER_IP#socket.gethostbyname(socket.gethostname())

class ChecksumFailed(Exception):
    pass

class TCP_Client:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))
        self.last_packet = -1
        print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    def execute(self):
        connected = True
        while connected:
            
            message = input("> ")

            self.client.send(message.encode(FORMAT))

            if(message == DISCONNECT_MSG):
                connected = False
            elif("GET" in message):
                split = message.split(' ')    
                if(len(split) > 1):
                    file_name = split[1]
                    self.get_request(file_name)
            elif("ACK" in message):
                print("You cannot send an ACK!")
                continue 
            else:
                server_msg = self.receive(True)  
                print(f"[SERVER] {server_msg}")

        self.client.close()

    def get_request(self, file_name):

        message = self.receive(True)

        print(f"[SERVER] {message}")

        old_checksum = self.receive()

        message = self.receive(True)

        split = message.split(' ')

        if(split[0] == "FOUND"):
            self.last_packet = 0
            print(message)
            packets = int(split[1])
            file = open(f"../duplicate/{file_name}", "wb+")
            while self.last_packet < packets:
                try:
                    self.ack_request(file_name, self.last_packet+1, file)
                except ChecksumFailed:
                    print(f'Checksum failed in packet: {self.last_packet+1}')
                except TimeoutError:
                    print(f'Timeout error in packet: {self.last_packet+1}')
                except Exception as e:
                    print(f'Error in packet {self.last_packet+1} -> {e}')
            print(f"Imported file: {file_name}")
            file.close()
            with open(f"../duplicate/{file_name}", 'rb') as f:
                new_checksum = calculate_sha_checksum(f.read())
            if(new_checksum != old_checksum):
                print(f"Invalid SHA checksum!")
                self.client.send((f"GET {file_name}").encode(FORMAT))
                self.get_request(file_name)
            else:
                print("Valid SHA Checksum!")
        elif(split[0] == "ERROR"):
            print(message)
            return
        else:
            print(f'Unknown message: {message}')
            return

    def ack_request(self, file_name, packet: int, file):
        msg = (f'ACK {file_name} {packet}').encode(FORMAT)

        self.client.send(msg)

        message = self.receive(True)

        #print(f"[SERVER] {message}")

        message = self.receive()

        content = message[PACKET_SIZE:]
        packet_part = struct.unpack(">q", message[0:PACKET_SIZE])[0]

        if packet_part != (self.last_packet + 1):
            print(f"Wrong package: {packet_part}")
            return
        
        print(f"Receiving package: {packet_part}")

        file.write(content)
        self.last_packet += 1


    def receive(self, isMessage: bool = False):
        msg = self.client.recv(BUFFER_SIZE)
        if(isMessage == True):
            msg = msg.decode(FORMAT)
        return msg

if __name__ == "__main__":
    client = TCP_Client()
    client.execute()