import hashlib

SERVER_IP = '192.168.0.50'
SERVER_PORT = 9999
BUFFER_SIZE = 512
DATA_SIZE = 492
CHECKSUM_SIZE = 16
PACKET_SIZE = 4
# MTU 64k UDP Datagram
# BUFFER_SIZE = PACKET(4), DATA(492), CHECKSUM(16)

def calculate_md5_checksum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.digest()