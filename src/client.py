import socket
import random
import struct 
from utils import SERVER_IP, SERVER_PORT, BUFFER_SIZE, DATA_SIZE, calculate_md5_checksum

class ChecksumFailed(Exception):
    pass

class UDP_Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_size = DATA_SIZE
        self.last_packet = -1
        self.corrupt = False
        self.packet_lost_probability = 20

    def execute(self):
        while True:
            message = input("")
            if message == "!q":
                self.client.close()
                break  
            elif("GET" in message):
                split = message.split(' ')                        
                if(len(split) > 1):
                    file_name = split[1]
                    self.corrupt = True if "CORRUPT" in message else False     
                    self.get_request(message.encode(), file_name)
                else:
                    print("Invalid arguments, try again!")
                    continue
            elif("ACK" in message):
                print("You cannot send an ACK!")
                continue
            else:
                print("Any instruction send, just message!")
                self.client.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
            
    def get_request(self, msg, file_name):
        self.client.sendto(msg, (SERVER_IP, SERVER_PORT))
        message, addr = self.receive()
        message = message.decode('utf-8')
        split = message.split(' ')
        if(split[0] == "FOUND"):
            self.last_packet = 0
            print(message)
            packets = int(split[1])
            file = open(f"../duplicate/{file_name}", "wb+")
            while self.last_packet < packets:
                try:
                    #time.sleep(1) #Para testar multiplos clientes
                    self.ack_request(file_name, self.last_packet+1, file)
                except ChecksumFailed:
                    print(f'Checksum failed in packet: {self.last_packet+1}')
                except TimeoutError:
                    print(f'Timeout error in packet: {self.last_packet+1}')
                except Exception as e:
                    print(f'Error in packet {self.last_packet+1} -> {e}')
            print(f"Imported file: {file_name}")
            file.close()
        elif(split[0] == "ERROR"):
            print(message)
            return
        else:
            print(f'Unknown message: {message}')
            return
     
    def ack_request(self, file_name, packet: int, file):
        msg = (f'ACK {file_name} {packet}').encode()
        self.client.sendto(msg, (SERVER_IP, SERVER_PORT))
        try:
            message, addr = self.receive()
            content = message[4:]
            packet_part = struct.unpack(">i", message[0:4])[0]
            if self.corrupt and random.randint(0,100) <= self.packet_lost_probability:
                print(f"Dropping packet: {packet_part}, asking to send again...")
                return
            elif packet_part != (self.last_packet + 1):
                print(f"Wrong package: {packet_part}")
                return
            print(f"Receiving package: {packet_part}")
            file.write(content)
            self.last_packet += 1
        except Exception as e:
            raise Exception(e)

    def receive(self):
        msg, addr = self.client.recvfrom(BUFFER_SIZE)
        checksum = msg[-16:]
        content = msg[:-16]
        message = content
        if(checksum != calculate_md5_checksum(message)):
            raise ChecksumFailed('Checksum not equal!')
        return message, checksum

if __name__ == "__main__":
    client = UDP_Client()
    client.execute()