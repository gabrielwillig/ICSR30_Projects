import socket
import threading
import queue
import io
#IP: 192.168.56.1

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

BUFFER = 32

def receive():
    while True:
        try:
            message, addr = server.recvfrom(2048)
            messages.put((message, addr))
        except:
            pass
def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            split = message.decode().split(' ')
            file = split[1:3]
            if(file == ['GET', '/file']):
                try:
                    fileName = message.decode().split("=")
                    fileName = fileName[1]
                    with open(f"{fileName}", "rb") as f:
                        contents = f.read()
                        for i in range(0,len(contents), BUFFER):
                            if(i + BUFFER > len(contents)):
                                substring = contents[i:]
                            else:
                                substring = contents[i:i+BUFFER]
                            print(substring, end="")
                            server.sendto(substring, client)
                            # with open(f"{fileName}", "wb+") as file:
                            #     while...:
                            #         file.write(contents)
                except Exception as e:
                    server.sendto(f"File not {fileName} found!".encode(), client)
                    continue
            else:    
                print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[message.decode().index(":")+1:]
                        server.sendto(f"{name} joined!".encode(), client)
                    else:
                        server.sendto(message, client)
                except:
                    clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()