import socket
import selectors
import os
import hashlib
import datetime

class MySocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None
        self.sentMessage = False

class ClientTCP:

    def __init__(self, server_address, server_port, num_clients):
        self.selector = selectors.DefaultSelector()
        self.num_clients = num_clients
        self.clients = []
        for i in range(num_clients):
            client_socket = self.create_client_socket(server_address, server_port)
            self.selector.register(client_socket, selectors.EVENT_WRITE | selectors.EVENT_READ, data=i)
            client_socket.data = i
            self.clients.append(client_socket)
        self.log_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-log.txt"
        os.makedirs("ArchivosRecibidos", exist_ok=True)
        os.makedirs("Logs", exist_ok=True)

    def create_client_socket(self, server_address, server_port):
        client_socket = MySocket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        return client_socket

    def read(self, client_socket, mask):
        client_id = client_socket.data
        file_hash = client_socket.recv(1024).decode()
        print(f'Hash received from server for client {client_id}: {file_hash}')

        file_size = client_socket.recv(1024).decode()
        file_size = int(file_size)
        print(f"File size received from server for client {client_id}: {file_size} bytes")

        with open(f"ArchivosRecibidos/Cliente{client_id+1}-Prueba-{self.num_clients}.txt", 'wb') as f:
            start_time = datetime.datetime.now()
            remaining_bytes = file_size
            while remaining_bytes > 0:
                chunk_size = min(4096, remaining_bytes)
                data = client_socket.recv(chunk_size)
                #print(f"Received {len(data)} bytes from server for client {client_id}.")
                f.write(data)
                remaining_bytes -= len(data)
            end_time = datetime.datetime.now()
            time_diff = end_time - start_time
            print(f"Received {file_size} bytes from server for client {client_id} in {time_diff.total_seconds()} seconds.")

            hash_obj = hashlib.sha256()
            with open(f.name, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    hash_obj.update(data)
            calculated_hash = hash_obj.hexdigest()
            if calculated_hash == file_hash:
                print(f"Hash of received file matches the hash received from server for client {client_id}.")
                status = "SUCCESS"
            else:
                print(f"Hash of received file does not match the hash received from server for client {client_id}.")
                status = "FAILED"
            with open(f"Logs/{self.log_filename}", 'a') as log_file:
                log_file.write(f"Client {client_id+1}: file=Cliente{client_id+1}-Prueba-{self.num_clients}.txt, size={file_size}, status={status}, time={time_diff.total_seconds()} seconds\n")

    def write(self, client_socket, mask):
        client_id = client_socket.data
        if mask is not None and not client_socket.sentMessage and mask & selectors.EVENT_WRITE:
            client_socket.send(b'Ready')
            client_socket.sentMessage = True

    def run(self):
        for i in range(self.num_clients):
            self.write(self.clients[i], None)

        while True:
            events = self.selector.select()
            if not events:
                break
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    self.read(key.fileobj, mask)
                if mask & selectors.EVENT_WRITE:
                    self.write(key.fileobj, mask)

        for key, mask in self.selector.get_map().items():
            key.fileobj.close()

if __name__ == '__main__':
    server_address = "127.0.0.1"
    server_port = 65432
    num_clients = 2

    client = ClientTCP(server_address, server_port, num_clients)
    client.run()


### NOW DO THE SAME BUT WITH THREADS
from threading import Thread