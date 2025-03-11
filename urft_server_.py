import sys
import os
import random
from socket import *

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverSocket.bind((serverName, serverPort))
DUPLICATION_RATE = 50

buffer = {}
expected_seq = 0
WINDOW_SIZE = 10

print(f"Server [{serverName}] พร้อมรับข้อมูล...")

file_name_msg, client_addr = serverSocket.recvfrom(1024)
file_name = file_name_msg.decode()
print(f"ได้รับชื่อไฟล์จาก Client: {file_name}")
serverSocket.sendto('ACK'.encode(), client_addr)  # ตอบรับ Client

# สร้างไฟล์ใหม่
with open(file_name[5:], "wb") as file:
    print(f"กำลังสร้างไฟล์: {file_name}")

    while True:
        print("Server กำลังอ่านไฟล์จาก Client")
        data_recv, client_addr = serverSocket.recvfrom(1030)
        # ตรวจจับการส่งชื่อไฟล์ซ้ำ
        if data_recv[:5].decode() == 'name:':
            print("ได้รับชื่อไฟล์ซ้ำ กำลังตอบกลับ Client...")
            serverSocket.sendto('ACK'.encode(), client_addr)
            continue
        # ตรวจจับจุดสิ้นสุดของไฟล์
        if data_recv == b'END':
            print("ไฟล์ถูกสร้างเสร็จสมบูรณ์!")
            break
        seq_num = int(data_recv[0:6].decode())
        file_data = data_recv[6:]
        if expected_seq <= seq_num < expected_seq + WINDOW_SIZE:
            buffer[seq_num] = file_data
            serverSocket.sendto(f"ACK {seq_num}".encode(), client_addr)
            
            while expected_seq in buffer:
                if buffer[expected_seq] != b'END':
                    file.write(buffer[expected_seq])
                del buffer[expected_seq]
                expected_seq += 1  # เลื่อนหน้าต่าง
        elif expected_seq - WINDOW_SIZE <= seq_num < expected_seq:
            serverSocket.sendto(f"ACK {seq_num}".encode(), client_addr)
        else:
            pass
        
serverSocket.close()
