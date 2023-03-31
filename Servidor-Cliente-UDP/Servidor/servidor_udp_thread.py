import datetime
import logging
import os
import socket
import time

server_address = ('localhost', 8000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(server_address)
BUFF_SIZE = 65507

def init_logger():
    log_dir = 'Servidor-Cliente-UDP/Servidor/Logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'
    logging.basicConfig(filename=f'Servidor-Cliente-UDP/Servidor/Logs/{log_filename}', level=logging.INFO)
    return logging.getLogger()

logger = init_logger()

def send_file_udp(id, file_size, client_address):
    # Send the file size we want to the server with a sequence number
    sequence_number = 0
    if file_size == 1:
        file_name = "100MB.bin"
        file_size = os.path.getsize(f"files/{file_name}")
    else:
        file_name = "250MB.bin"
        file_size = os.path.getsize(f"files/{file_name}")

    while True:
        sequence_number += 1
        data = f"{sequence_number}:{file_size}:{id}"
        server_socket.sendto(data.encode(), client_address)
        print(f"Sent packet {file_size} to client at {client_address} with client id {id}")
        break
    
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
        print(f"Sent file {file_name} of {file_size} bytes to client {id} at {client_address} and sent {bytes_sent} bytes in total.")

    # Log the time it took to send the file
    total = end - start
        
    logger.info(f"Sent file {file_name} of {file_size} bytes to client {id} at {client_address} and sent {bytes_sent} bytes in total. Took {total} seconds to send the file.")
    # Send an empty packet to signal the end of the file
    server_socket.sendto(b'', client_address)
    print(f"Sent end of file to client at {client_address} with client id {id}")
        

try:
    print("Server is listening on port 8000")
    print("Waiting for client to connect...")
    while True:
        # Create a dictionary to store received packets
        received_packets = {}
        client_id = None

        while True:
            # Receive a packet from the client
            packet, client_address = server_socket.recvfrom(1024)

            # Extract the client id and sequence number from the packet
            parts = packet.decode().split(':', 2)
            if len(parts) == 3:
                client_id = int(parts[2])
                sequence_number = int(parts[0])
                message = parts[1]
                print(f"Received packet {sequence_number} from client {client_id} at {client_address}: {message}")
            else:
                print(f"Received invalid packet from {client_address} with client id {client_id}: {packet.decode()}")
                continue

            # Store the packet in the dictionary
            received_packets[sequence_number] = message

            # # Send an acknowledgement for this packet
            # server_socket.sendto(f"ACK:{sequence_number}:{client_id}".encode(), client_address)

            # Send the file
            if message == "1" or message == "2":
                send_file_udp(client_id, int(message), client_address)
                break

except KeyboardInterrupt:
    print("Server shutting down...")
    server_socket.close()