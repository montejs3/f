import datetime
import logging
import os
import socket
import struct
import time
from socket import SO_REUSEADDR, SOCK_DGRAM, SOCK_STREAM, error, socket, SOL_SOCKET, AF_INET

host = 'localhost'
server_address_tcp = (host, 5000)
server_address_udp = (host, 8000)
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(server_address_udp)
BUFF_SIZE = 65507

# Create a server TCP socket and allow address re-use
s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind(server_address_tcp)

def init_logger():
    log_dir = 'Servidor-Cliente-UDP/Servidor/Logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'
    logging.basicConfig(filename=f'Servidor-Cliente-UDP/Servidor/Logs/{log_filename}', level=logging.INFO)
    return logging.getLogger()

logger = init_logger()

def send_file_udp(id, file_size, client_address, sock):

    if file_size == 1:
        file_name = "100MB.bin"
        file_size = os.path.getsize(f"files/{file_name}")
    else:
        file_name = "250MB.bin"
        file_size = os.path.getsize(f"files/{file_name}")

    while True:
        data = f"{file_size}:{id}"
        sock.send(data.encode())
        print(f"Paquete enviado {file_size} al cliente con la direccion {client_address} con cliente id {id}")
        break

    port_bytes = sock.recv(4)
    port_to_use = struct.unpack('>i', port_bytes)[0]
    
    client_address = (client_address[0], port_to_use)
    bytes_sent = 0
    # Send the file contents
    with open(f"files/{file_name}", "rb") as f:
        start = time.monotonic()
        while True:
            data = f.read(BUFF_SIZE)
            if not data:
                break
            server_socket.sendto(data, client_address)
            bytes_sent += len(data)
        end = time.monotonic()
        # Log the time it took to send the file
        total = end - start
        print(f"Archivo enviado {file_name} de {file_size} bytes al cliente {id} con direccion {client_address} y enviados {bytes_sent} bytes en total. Tomo {total} segundos en enviar el archivo.")
        
    logger.info(f"Archivo enviado {file_name} de {file_size} bytes al cliente {id} con direccion {client_address} y enviados {bytes_sent} bytes en total. Tomo {total} segundos en enviar el archivo.")
    # Send an empty packet to signal the end of the file
    server_socket.sendto(b'', client_address)
    print(f"Enviada la terminacion del archivo al cliente con direccion {client_address} y cliente id {id}")
        

try:
    print("Servidor escuchando en el puerto 8000 y TCP en el puerto 5000...")
    print("Esperando peticiones de los clientes...")
    while True:
        client_id = None

        while True:
            # Listen for a request
            s.listen()
            # Accept the request
            sock, client_address = s.accept()
            # Receive a packet from the client
            packet = sock.recv(1024)

            # Extract the client id and sequence number from the packet
            parts = packet.decode().split(':')
            if len(parts) == 2:
                client_id = int(parts[1])
                message = parts[0]
                print(f"Recibidos paquetes del cliente {client_id} con direccion {client_address}: {message}")
            else:
                print(f"Recibido paquete invalido de direccion {client_address} con cliente id {client_id}: {packet.decode()}")
                continue

            # Send the file
            if message == "1" or message == "2":
                send_file_udp(client_id, int(message), client_address, sock)
                break
        

except KeyboardInterrupt:
    print("Server shutting down...")
    server_socket.close()
    s.close()