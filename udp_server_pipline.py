import sys
import os
from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverName, serverPort))
DUPLICATION_RATE = 50
WINDOW_SIZE = 10

print(f"Server [{serverName}] พร้อมรับข้อมูล...")

file_name_msg, client_addr = serverSocket.recvfrom(1024)
file_name = file_name_msg.decode()[5:]
print(f"ได้รับชื่อไฟล์จาก Client: {file_name}")
serverSocket.sendto(b'ACK', client_addr)  # ตอบรับ Client

# สร้างไฟล์ใหม่
with open(file_name, "wb") as file:
    print(f"กำลังสร้างไฟล์: {file_name}")

    buffer = {}
    expected_seq = 0

    while True:
        data_recv, client_addr = serverSocket.recvfrom(1030)
        # ตรวจจับการส่งชื่อไฟล์ซ้ำ
        if data_recv[:5].decode() == 'name:':
            print("ได้รับชื่อไฟล์ซ้ำ กำลังตอบกลับ Client...")
            serverSocket.sendto(b'ACK', client_addr)
            continue
        # ตรวจจับจุดสิ้นสุดของไฟล์
        if data_recv == b'END':
            print("ไฟล์ถูกสร้างเสร็จสมบูรณ์!")
            break
        try:
            seq_num = int(data_recv[:6].decode())
            file_data = data_recv[6:]
        except ValueError:
            print("ข้อมูลเสียหาย ข้ามแพ็กเก็ตนี้")
            continue

        if expected_seq <= seq_num < expected_seq + WINDOW_SIZE:
            buffer[seq_num] = file_data
            serverSocket.sendto(f"ACK {seq_num}".encode(), client_addr)

            while expected_seq in buffer:
                if buffer[expected_seq] != b'END':
                    file.write(buffer[expected_seq])
                del buffer[expected_seq]
                expected_seq += 1

        elif expected_seq - WINDOW_SIZE <= seq_num < expected_seq:
            serverSocket.sendto(f"ACK {seq_num}".encode(), client_addr)

serverSocket.close()
print("Server ปิดการเชื่อมต่อ")
