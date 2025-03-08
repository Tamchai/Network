from socket import *
import sys
import os
import time

file_path = sys.argv[1]
serverName = sys.argv[2]
serverPort = int(sys.argv[3])

DUPLICATION_RATE = 0.3
TIMEOUT = 0.02
PACKET_SIZE = 1024
WINDOW_SIZE = 10
MAX_RETRIES = 5

file_name = "name:" + os.path.basename(file_path)
file_path = file_path.replace("\\", "/")
packets = []

with open(file_path, 'rb') as file:
    while chunk := file.read(PACKET_SIZE):
        packets.append(chunk)
packets.append(b"END")

total_packets = len(packets)
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(TIMEOUT)
print(f"กำลังส่งไฟล์: {file_name}, จำนวนแพ็กเก็ตทั้งหมด: {total_packets}")

while True:
    try:
        clientSocket.sendto(file_name.encode(), (serverName, serverPort))
        clientSocket.recvfrom(16)  # รอ ACK จากเซิร์ฟเวอร์
        break
    except timeout:
        print("ไม่ได้รับ ACK จากเซิร์ฟเวอร์ กำลังส่งชื่อไฟล์ใหม่...")

window_base = 0
window = {}
retries = {}

while window_base < total_packets:
    for seq_num in range(window_base, min(window_base + WINDOW_SIZE, total_packets)):
        if seq_num not in window:
            packet = f"{seq_num:06}".encode() + packets[seq_num]
            clientSocket.sendto(packet, (serverName, serverPort))
            window[seq_num] = time.time()
            retries[seq_num] = 0
    try:
        ack, _ = clientSocket.recvfrom(1024)
        ack_num = int(ack.decode().split()[1])

        if ack_num in window:
            del window[ack_num]
            retries.pop(ack_num, None)

        while window_base in window:
            window_base += 1

    except timeout:
        for seq_num in list(window.keys()):
            if time.time() - window[seq_num] > TIMEOUT:
                if retries[seq_num] < MAX_RETRIES:
                    packet = f"{seq_num:06}".encode() + packets[seq_num]
                    clientSocket.sendto(packet, (serverName, serverPort))
                    window[seq_num] = time.time()
                    retries[seq_num] += 1
                else:
                    print(f"แพ็กเก็ต {seq_num} ส่งซ้ำเกินขีดจำกัด!")

clientSocket.sendto(b"END", (serverName, serverPort))
print("ไฟล์ถูกส่งครบถ้วน!")

clientSocket.close()
