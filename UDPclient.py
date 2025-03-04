from socket import *
from sys import *

file_path = "test.txt"
# server_ip = sys.argv[2]
# server_port = int(sys.argv[3])
serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET,SOCK_DGRAM)

BUFFER_SIZE = 1024


try:
    # ส่งชื่อไฟล์ไปยัง server
    filename = file_path.split("/")[-1]
    clientSocket.sendto(filename.encode(), (serverName, serverPort))
    
    # เปิดไฟล์และอ่านข้อมูลส่งไปยัง server
    with open(file_path, "rb") as file:
        while chunk := file.read(BUFFER_SIZE):
            clientSocket.sendto(chunk, (serverName, serverPort))
    
    # ส่งสัญญาณ EOF เพื่อแจ้งจบการส่งข้อมูล
    clientSocket.sendto(b"EOF", (serverName, serverPort))
    print("File sent successfully.")
finally:
    clientSocket.close()