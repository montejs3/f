import datetime
import socket
import threading
import time
BUFF_SIZE = 65507
log_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-log.txt"

def receive_file(client_socket, file_size, client_id, num_clients):
    file_name = f"ArchivosRecibidos/Cliente{client_id+1}-Prueba-{num_clients}.txt"
    file_size2 = file_size
    # Reescribimos el archivo en un archivo con el nombre "Cliente"
    check_sum = 0
    with open(file_name, 'wb') as f:
        start_time = time.monotonic()
        while file_size > 0:
            data, _ = client_socket.recvfrom(BUFF_SIZE)
            # Revisamos el fin del archivo
            if len(data) == 0:
                break
            f.write(data)
            file_size -= len(data)
            check_sum += len(data)
        end_time = time.monotonic()
        # Calcular el tiempo total de recepción
        tiempo_total = end_time - start_time
        with open(f"Logs/{log_filename}", 'a') as log_file:
            log_file.write(f"Client {client_id+1}: file=Cliente{client_id+1}-Prueba-{num_clients}.txt, size={file_size2}, status=SUCCESS, time={tiempo_total} seconds\n")

    
    if check_sum == file_size:
        data, _ = client_socket.recvfrom()
    

    print(f"Received file from server for client {client_id} in {tiempo_total} seconds.")

def send_message(id, host, port, message, num_clients):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the file size we want to the server with a sequence number
    sequence_number = 0
    while True:
        sequence_number += 1
        data = f"{sequence_number}:{message}:{id}"
        client_socket.sendto(data.encode(), (host, port))
        print(f"Sent client id {id} and file size {message} to server at {host}:{port}")

        # Receive the file
        # Extract the client id and sequence number from the packet
        packet, server_address = client_socket.recvfrom(1024)
        parts = packet.decode().split(':', 2)
        if len(parts) == 3:
            client_id = int(parts[2])
            sequence_number = int(parts[0])
            file_size = parts[1]

        receive_file(client_socket, int(file_size), client_id, num_clients)
        break

    client_socket.close()

try:
    if __name__ == '__main__':
        host = 'localhost'
        port = 8000
        file_num = input("Enter the file number to send (1 for 100MB or 2 for 250MB): ")
        num_clients = int(input("Enter the number of clients to send the file to (Max 25): "))

        if file_num != '1' and file_num != '2':
            print("Invalid file number")
            exit()

        if num_clients > 25:
            print("Max number of clients is 25")
            exit()

        # create 10 threads and send messages concurrently
        for i in range(num_clients):
            thread = threading.Thread(target=send_message, args=(i, host, port, file_num, num_clients))
            thread.start()

except KeyboardInterrupt:
    print("Keyboard interrupt")
    exit()