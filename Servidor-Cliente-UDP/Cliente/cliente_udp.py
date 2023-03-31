import socket
import os
import logging
from datetime import datetime
import threading

import socket
import threading
import time

buffeSize = 65507 
numConexiones = 10
CLIENTE_IP = '127.0.0.1'
CLIENTE_PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect((CLIENTE_IP, CLIENTE_PORT))

def send_file_request(filename, server_address):
    client_socket.sendto(filename.encode(), server_address)

def receive_file(client_socket, file_size):
    # Reescribimos el archivo en un archivo con el nombre "Cliente"
    with open('ArchivosRecibidos/cliente.txt', 'wb') as f:
        start_time = time.monotonic()
        while file_size > 0:
            data, _ = client_socket.recvfrom(buffeSize)
            f.write(data)
            file_size -= len(data)
        end_time = time.monotonic()
    
    # Calcular el tiempo total de recepción
    tiempo_total = end_time - start_time

def download_file(id, filename, server_address):
    send_file_request(filename, server_address)
    fileSize = client_socket.recvfrom(buffeSize)
    receive_file(client_socket, int(fileSize))

    client_socket.close()

def main():
    print("Starting client")
    filename = input("Enter the file number to send (1 for 100MB or 2 for 250MB): ")
    threads = []
    for i in range(numConexiones):
        t = threading.Thread(target=download_file, args=(i, filename, (CLIENTE_IP, CLIENTE_PORT)))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == '__main__':
    main()