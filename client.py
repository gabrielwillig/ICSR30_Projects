import socket
import threading
import random

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

name = input("Nickname: ")

BUFFER = 32

def receive():
    while True:
        try:
            message, _ = client.recvfrom(BUFFER)
            print(message.decode())
        except:
            pass

t = threading.Thread(target=receive)
t.start()

client.sendto(f"SIGNUP_TAG: {name}".encode(), ("localhost", 9999))

while True:
    message = input("")
    if message == "!q":
        exit()
    # elif message.startswith("GET /file"):
    #     split = message.split(' ')
    #     file = split[2]
    #     client.sendto(f"{name} requested GET: {file}".encode(), ("localhost", 9999))
    # GET /file --filename=filename.txt
    else:
        client.sendto(f"{name}: {message}".encode(), ("localhost", 9999))