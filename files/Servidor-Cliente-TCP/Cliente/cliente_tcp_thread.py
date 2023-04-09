from socket import SO_REUSEADDR, SOCK_STREAM, error, socket, SOL_SOCKET, AF_INET
import logging
import hashlib
import datetime
import struct
from threading import Thread
from queue import Queue

class ClientThread:
    def __init__(self, id, address, port, log_filename, file_number):
        self.id = id
        self.address = address
        self.port = port
        self.s = socket(AF_INET, SOCK_STREAM)
        self.log_filename = log_filename
        self.file_number = file_number


    def run(self):
        global num_clients
        try:
            # Allow socket address reuse
            self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Connect to the ip over the given port
            self.s.connect((self.address, self.port))

            # Pack the integer into a bytes object using big-endian byte order
            id_bytes = struct.pack('>i', self.id)
            # Send the bytes object over the socket
            self.s.send(id_bytes)

            # Send the file size we want
            self.s.send(file_num.encode())

            response_server = self.s.recv(1024).decode()
            # Send the defined request message
            message = "Ready"

            if response_server == "ok":
                self.s.send(message.encode())
                print(f'Cliente {self.id} ha enviado el mensaje de preparado')

                # Receive the padded file hash
                file_hash_padded = self.s.recv(1024).decode()

                # Strip any trailing null bytes from the received string
                file_hash = file_hash_padded.rstrip('\x00')
                print(f'Hash recibido del servidor por el cliente {self.id}: {file_hash}')

                # Receive the file size
                data = self.s.recv(8)
                file_size = struct.unpack("!Q", data)[0]
                print(f"Tamanio del archivo recibido del servidor por el cliente {self.id}: {file_size} bytes")

                self.receive_file(file_size, file_hash, num_clients)
                
                self.s.close()
            
            else:
                self.s.close()
            
        except error as e:
            print(e)
            raise(e)


    def receive_file(self, file_size, file_hash, num_clients):
        
        client_id = self.id

        file_name = f"ArchivosRecibidos/Cliente{client_id+1}-Prueba-{num_clients}.txt"

        with open(file_name, 'wb') as f:
            start_time = datetime.datetime.now()
            remaining_bytes = file_size
            while remaining_bytes > 0:
                chunk_size = min(1024, remaining_bytes)
                data = self.s.recv(chunk_size)
                #print(f"Received {len(data)} bytes from server for client {client_id}.")
                f.write(data)
                remaining_bytes -= len(data)
            end_time = datetime.datetime.now()
            time_diff = end_time - start_time
            print(f"Recibidos {file_size} bytes del servidor por el cliente {client_id} en {time_diff.total_seconds()} segundos.")

            # Send EOF message to server
            self.s.send("EOF".encode())

        # Calculate the hash of the received file
        calculated_hash = hashlib.md5(open(file_name, 'rb').read()).hexdigest()
        print(f"Hash del archivo recibido por el cliente {client_id}: {calculated_hash}")

        if calculated_hash == file_hash:
            print(f"Hash del archivo recibido es igual al hash recibido del servidor por el cliente {client_id}.")
            status = "SUCCESS"
        else:
            print(f"Hash del archivo recibido NO es igual al hash recibido del servidor por el cliente {client_id}.")
            status = "FAILED"
        with open(f"Logs/{self.log_filename}", 'a') as log_file:
            log_file.write(f"Cliente {client_id+1}: Archivo=Cliente{client_id+1}-Prueba-{num_clients}.txt, Tamanio={file_size}, Estado={status}, puerto={self.s.getsockname()[1]}, tiempo={time_diff.total_seconds()} segundos\n")


# Create a queue to hold the tasks for the worker threads
q = Queue(maxsize=0)

print("--Client app iniciado--")
num_clients = int(input("Ingrese el numero de clientes que solicitaran archivos al servidor (MAX = 25): "))

# End the program if the number of clients is greater than 25
if num_clients > 25:
    print("El numero maximo de clientes es 25!")
    exit()

file_num = input("Ingrese el numero del archivo a enviar (1 para 100MB o 2 para 250MB): ")

def worker():
    while True:
        try:
            item = q.get()
            client = ClientThread(item, "127.0.0.1", 5000, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-log.txt", file_num)
            client.run()
        except Exception as e:
            logging.exception(f"Exception in worker: {e}")
        finally:
            q.task_done()

for item in range(num_clients):
    q.put(item)

for i in range(num_clients):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

# Do not exit the main thread until the sub-threads complete their work queue
q.join()