import socket
import math
import struct
from utils import SERVER_IP, SERVER_PORT, BUFFER_SIZE, CHECKSUM_SIZE, DATA_SIZE, PACKET_SIZE, calculate_md5_checksum

class UDP_Server:
     
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((SERVER_IP, SERVER_PORT))
        self.buffer_size = BUFFER_SIZE
        self.checksum_size = CHECKSUM_SIZE
        self.packet_size = PACKET_SIZE
        self.data_size = DATA_SIZE

    def execute(self):
        while True:
            try:
                message, addr = self.server.recvfrom(self.buffer_size)
                decoded = message.decode()
                print(decoded)
                split = decoded.split(' ')
                if(len(split) > 1):
                    file_name = split[1]
                    if(split[0] == "GET"):
                        self.get_request(addr, file_name)
                    elif(split[0] == "ACK"):
                        packet = int(split[2])
                        self.ack_request(addr, file_name, packet)
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
    

    def get_request(self, addr, file_name):
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                packets = math.ceil(len(content)/self.data_size)
                message = f'FOUND {packets} packets!'
        except FileNotFoundError:
            message = f'ERROR File: {file_name} not found!'    
        except Exception as e:
            message = f'ERROR {e}!'
        finally:
            self.broadcast(message, addr)

    def ack_request(self, addr, file_name, packet: int):
        try:
            with open(f"../assets/{file_name}", 'rb') as f:
                content = f.read()
                packets = math.ceil(len(content)/self.data_size)
                if packet > packets:
                    message = 'ERROR exceeded maximum packet number'
                else:
                    start = self.data_size * (packet - 1)
                    end = start + self.data_size
                    response = content[start:end]
                    message = struct.pack(">i", packet) + response
        except FileNotFoundError:
            message = f'ERROR File {file_name} not found!'    
        except Exception as e:
            message = f'ERROR {e}!'
        finally:
            self.broadcast(message, addr)

    def broadcast(self, msg, addr):
        print(msg)
        if type(msg) is str:
            msg = bytes(msg, 'utf-8')
        checksum = calculate_md5_checksum(msg)
        message = msg + checksum
        self.server.sendto(message, addr)

if __name__ == "__main__":
    server = UDP_Server()
    server.execute()