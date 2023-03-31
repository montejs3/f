import datetime
import logging
import os
import socket
import sys
import threading
import time

buffeSize = 65507 
file1 = "files/100MB.bin"
file2 = "files/250MB.bin"
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
threads = []

def init_logger():
    log_dir = 'Servidor-Cliente-UDP/Servidor/Logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'
    logging.basicConfig(filename=f'Servidor-Cliente-UDP/Servidor/Logs/{log_filename}', level=logging.INFO)
    return logging.getLogger()

logger = init_logger()

def handle_client_request(file1, file2, filenum):
    
    # Recibir el nombre del archivo solicitado
    print(f"Message received from client")
    filenum = int(filenum)

    # Enviar el archivo requerido
    if filenum == 1:
        file_size = os.path.getsize(file1)
        print(f"Sending file size to client {file_size}")
        # Se envia el file size
        server_socket.sendto(str(file_size).encode(), (SERVER_IP, SERVER_PORT))
        with open(file1, 'rb') as f:
            data = f.read(buffeSize)
            start_time = time.monotonic()  # Tiempo de inicio del envío
            while data:
                server_socket.sendto(data, (SERVER_IP, SERVER_PORT))
                data = f.read(buffeSize)
            end_time = time.monotonic()  # Tiempo de fin del envío

        # Calcular el tiempo total de envío
        tiempo_total = end_time - start_time   

        # Registrar en el archivo de log los detalles de la conexión
        logger.info(f"Requested 100MB.bin")
        logger.info(f"File succesfuly sent to client in {tiempo_total} with size {file_size} bytes")


    # Enviar el archivo requerido
    if filenum == 2:
        file_size = os.path.getsize(file2)
        print(f"Sending file size to client {file_size}")
        with open(file2, 'rb') as f:
            data = f.read(buffeSize)
            start_time = time.monotonic()  # Tiempo de inicio del envío
            while data:
                server_socket.sendto(data, (SERVER_IP, SERVER_PORT))
                data = f.read(buffeSize)
            end_time = time.monotonic()  # Tiempo de fin del envío

        # Calcular el tiempo total de envío
        tiempo_total = end_time - start_time
        
        # Registrar en el archivo de log los detalles de la conexión
        logger.info(f"Requested 250MB.bin")
        logger.info(f"File succesfuly sent to client in {tiempo_total} with size {file_size} bytes")


    else:
        print('Invalid filename requested')

def main():
    
    print("Starting server")
    while True:
        filenum = server_socket.recv(buffeSize).decode()
        t = threading.Thread(target=handle_client_request, args=(file1, file2, filenum))
        t.start()
        threads.append(t)
    


if __name__ == '__main__':
    main()

    for item in threads:
        item.join()


