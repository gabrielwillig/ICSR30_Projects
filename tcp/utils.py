import hashlib

PORT = 9999
FORMAT = 'utf-8'
PACKET_SIZE = 8
CHECKSUM_SIZE = 16
BUFFER_SIZE = 1024
DATA_SIZE = BUFFER_SIZE - PACKET_SIZE
DISCONNECT_MSG = "!q"
SERVER_IP = "192.168.0.50"

# BUFFER_SIZE = PACKET(8), DATA(), CHECKSUM(32)

def calculate_sha_checksum(data):
    sha = hashlib.sha256()
    sha.update(data)
    return sha.digest()