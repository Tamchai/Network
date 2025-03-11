from socket import *
import sys
import os
import random
import time

file_path = str(sys.argv[1])
serverName = str(sys.argv[2])
serverPort = int(sys.argv[3])

DUPLICATION_RATE = 0.3
timeout = 0.02
packet_size = 1024

file_name = "name:" + os.path.basename(file_path)
packets = []
if "\\" in str(file_path):
    file_path = file_path.replace("\\", "/")


with open(file_path, 'rb') as file:
    while data := file.read(packet_size):
        if not data:
            packets.append(b"END")
            break
        packets.append(data)
total_packets = len(packets)

window_base = 0
window_size = 10
window = {}
retries = {}
max_retries = 5

print(f"กำลังส่งไฟล์: {file_name}, จำนวนแพ็กเก็ตทั้งหมด: {total_packets}")
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.sendto(file_name.encode(),(serverName,serverPort))
clientSocket.settimeout(timeout)

while True:
    try:
        clientSocket.recvfrom(16) 
        while window_base < total_packets:
            for seq_num in range(window_base, min(window_base + window_size, total_packets)):
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
                    window_base = min(window) if window else ack_num + 1
            except :
                # ตรวจสอบแพ็กเก็ตที่ Timeout และทำการส่งซ้ำ
                for seq in list(window.keys()):
                    if time.time() - window[seq] > timeout:
                        if retries[seq] < max_retries:
                            packet = f"{seq:06}".encode() + packets[seq]
                            clientSocket.sendto(packet, (serverName,serverPort))
                            window[seq] = time.time()
                            retries[seq] += 1
                        else:
                            print(f"แพ็กเก็ต {seq} ส่งซ้ำเกินขีดจำกัด!")

        if window_base >= total_packets:
            print("ไฟล์ถูกส่งครบถ้วน!")
            clientSocket.sendto(b"END", (serverName, serverPort))
            break
        clientSocket.close()
        break
    except:
        #ถ้าไม่มีการตอบ ACK กลับมาตามเวลาที่กำหนด
        clientSocket.sendto(file_name.encode(),(serverName,serverPort))
        clientSocket.settimeout(timeout)
        continue
