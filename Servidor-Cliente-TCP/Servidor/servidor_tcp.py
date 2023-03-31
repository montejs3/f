import hashlib
import select
import socket
import selectors
import sys
import signal
import os
import logging
import time


class FileServer:
    def __init__(self, host, port, max_clients, log_file):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.selector = selectors.DefaultSelector()
        self.server_socket = None
        self.clients = {}
        self.log_file = log_file
        self.logger = None
        self.file_size = None
        self.file_name = None
        self.file_hash = None

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f'Server ready and listening on {self.host}:{self.port}')
            self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)
            self.init_logger()
        except socket.error as e:
            print(f'Error creating socket: {e}')
            sys.exit(1)

    def init_logger(self):
        log_dir = 'Servidor-Cliente-TCP/Servidor/Logs'
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        log_file_path = f"{log_dir}/{self.log_file}_{time.strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger()

    def accept(self, sock, mask):
        if len(self.clients) >= self.max_clients:
            return

        conn, addr = sock.accept()
        conn.setblocking(False)
        print(f'Accepted connection from {addr}')
        self.logger.info(f'Accepted connection from {addr}')

        # send hash value to client
        conn.send(self.file_hash.encode())

        # send file size to client
        conn.send(str(self.file_size).encode())

        # register client socket for read events
        self.selector.register(conn, selectors.EVENT_READ, data={'file_name': self.file_name})

        # add client to list of clients
        self.clients[conn] = {'addr': addr, 'file_name': self.file_name, 'ready': False}

        # check if all clients are ready to receive file
        if len(self.clients) == self.max_clients and all(self.clients[c].get('ready', True) for c in self.clients):
            self.send_file()

    def read(self, conn, mask):
        data = conn.recv(1024)
        if data:
            print(data.decode() + "\n")
            if data == b'Ready':
                self.clients[conn]['ready'] = True

                # check if all clients are ready to receive file
                if len(self.clients) == self.max_clients and all(self.clients[c].get('ready', True) for c in self.clients):
                    self.send_file()
        else:
            print(conn)
            print(f'Closing connection to {conn.getpeername()}')
            self.selector.unregister(conn)
            conn.close()
            self.logger.info(f'Connection closed to {conn.getpeername()}')

            # remove client from list of clients
            del self.clients[conn]

    def write(self, conn, mask):

        # check if all clients are ready to receive file
        if len(self.clients) == self.max_clients and all(self.clients[c].get('ready', True) for c in self.clients):
            self.send_file()

    def send_file(self):
        # send file to clients
        with open(self.file_name, 'rb') as f:
            for c in self.clients:
                portion = f.read(self.file_size)
                c.send(portion)
            
        # close all connections
        for c in self.clients:
            self.logger.info(f'Connection closed to {c.getpeername()}')
            self.selector.unregister(c)
            c.close()
            
    
        # clear list of clients
        self.clients.clear()

    def run(self):
        try:
            while True:
                events = self.selector.select(timeout=1)
                for key, mask in events:
                    if key.data is None:
                        self.accept(key.fileobj, mask)
                    else:
                        if mask & selectors.EVENT_READ:
                            self.read(key.fileobj, mask)
                        if mask & selectors.EVENT_WRITE:
                            self.write(key.fileobj, mask)
        except KeyboardInterrupt:
            self.stop()
                    
    def stop(self):
        self.selector.close()
        self.server_socket.close()
        print('Server stopped')
        self.logger.info('Server stopped')

    
if __name__ == '__main__':

    host = "127.0.0.1"
    port = 65432
    max_clients = 2
    log_file = 'server'
    server = FileServer(host, port, max_clients, log_file)
    server.start()

    # get file name and size
    server.file_name = input('Enter file number: (1 for 100MB, 2 for 250MB)')
    if server.file_name == '1':
        print('File 1 selected - 100MB.bin')
        server.file_name = 'files/100MB.bin'

    elif server.file_name == '2':
        print('File 2 selected - 250MB.bin')
        server.file_name = 'files/250MB.bin'

    server.file_size = os.path.getsize(server.file_name)

    # get hash value of file
    with open(server.file_name, 'rb') as f:
        server.file_hash = hashlib.sha256(f.read()).hexdigest()

    server.run()
