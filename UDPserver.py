from socket import *

server_ip = "127.0.0.1"
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_DGRAM)
serverSocket.bind((server_ip,serverPort))
print(f"Server listening on {server_ip}:{serverPort}")

data,client_addr = serverSocket.recvfrom(1024)
filename = data.decode()
print(f"Receiving file: {filename} from {client_addr}")

with open(filename,"wb") as file:
    while True:
        data, _ = serverSocket.recvfrom(1024)
        if data == b"EOF":
            break
        file.write(data)
print("File received successfully.")
serverSocket.close()