from socket import SO_REUSEADDR, SOCK_STREAM, error, socket, SOL_SOCKET, AF_INET
import logging
import hashlib
import os
import datetime
import struct
from threading import Thread, Lock
import time

thread_lock = Lock()

# Create a server TCP socket and allow address re-use
s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 5000))

# Create a list in which threads will be stored in order to be joined later
threads = []

def init_logger():
    log_dir = 'Servidor-Cliente-TCP/Servidor/Logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-log.txt'
    logging.basicConfig(filename=f'Servidor-Cliente-TCP/Servidor/Logs/{log_filename}', level=logging.INFO)
    return logging.getLogger()

logger = init_logger()

class RequestHandler(Thread):
    def __init__(self, addr, port, s, lock):
        Thread.__init__(self)
        self.port = port
        self.addr = addr
        self.s = s
        self.lock = lock
        self.file_num = 0
        self.msg = ""

    def run(self):

        global logger

        # Get the ID of the client
        id_bytes = self.s.recv(4)
        client_id = struct.unpack('>i', id_bytes)[0]
        print(f"Client ID received from client {client_id}")

        file_name_msg = int(self.s.recv(1024).decode())

        if file_name_msg == 1:
            self.file_num = 1
            logger.info(f"Client {client_id} requested 100MB.bin")
        
        elif file_name_msg == 2:
            self.file_num = 2
            logger.info(f"Client {client_id} requested 250MB.bin")
        
        self.s.send("ok".encode())
        logger.info(f"Sending 'ok' to client {client_id}")
        
        self.msg = self.s.recv(1024).decode()

        if self.msg == "Ready":
            self.send_file(logger, client_id)
            logger.info(f"Client {client_id} is ready to receive the file")
        else: 
            print("Message not recognized")
            logger.info(f"Message not recognized from client {client_id}")

        
        # Close the connection
        self.s.close()


    def send_file(self, logger, client_id):
        
        if self.file_num == 1:
            file_name = "files/100MB.bin"
        
        elif self.file_num == 2:
            file_name = "files/250MB.bin"

        file_hash = hashlib.md5(open(file_name, 'rb').read()).hexdigest()
        logger.info(f"File hash calculated for client {client_id} : {file_hash}")

        # Pad the file hash with null bytes to ensure it is exactly 1024 bytes
        file_hash_padded = file_hash.ljust(1024, '\x00')

        # Send the padded file hash
        self.s.send(file_hash_padded.encode())

        # Send the file size
        file_size = os.path.getsize(file_name)
        print(f"Sending file size to client {client_id} : {file_size}")
        self.s.send(struct.pack("!Q", file_size))

        # Send the file
        with open(file_name, 'rb') as f:
            start_time = datetime.datetime.now()
            remaining_bytes = file_size
            while remaining_bytes > 0:
                # Send 1024 bytes at a time
                data = f.read(1024)
                self.s.send(data)
                remaining_bytes -= 1024
            
            # Get eof message from client
            eof_msg = self.s.recv(1024).decode()
            if eof_msg == "EOF":
                end_time = datetime.datetime.now()
                print(f"File sent to client {client_id} in {end_time - start_time}")
                # Log the time it took to send the file
                logger.info(f"File succesfuly sent to client {client_id} in {end_time - start_time} with size {file_size} bytes")
            else:
                end_time = datetime.datetime.now()
                print(f"File not sent to client {client_id} in {end_time - start_time}")
                # Log the time it took to send the file
                logger.info(f"File not succesfuly sent to client {client_id} in {end_time - start_time} with size {file_size} bytes")


print("Starting server")
while True:
    try:
        print("Waiting for a client request")
        # Listen for a request
        s.listen()
        # Accept the request
        sock, addr = s.accept()

        # Spawn a new thread for the given request
        newThread = RequestHandler(addr[0], addr[1], sock, thread_lock)
        newThread.start()
        threads.append(newThread)

    except KeyboardInterrupt:
        print ("\nExiting Server\n")
        break

for item in threads:
    item.join()