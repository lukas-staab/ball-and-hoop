import time
import socket
from threading import Thread

import numpy as np

from src.serial import SerialCom


class Server(Thread):
    def __init__(self, server_ip, server_port, print_debug=False):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.stop = False
        self.print_debug = print_debug
        # self.serial = SerialCom()
        self.values = {}
        print('Init Server')

    def __enter__(self):
        self.socket.__enter__()
        # setup websocket
        self.socket.bind((self.server_ip, self.server_port))
        self.print('Server binding')

        # backlog with 1 unaccepted connection

        self.start()
        return self

    def run(self) -> None:
        self.print('Server is waiting for connections')
        self.socket.settimeout(20)
        self.socket.listen(2)
        while not self.stop:
            try:
                # wait for new connection
                while len(self.connections) < 2:
                    conn, addr = self.socket.accept()
                    self.print(str(addr) + ': connection accepted')
                    conn.__enter__()
                    self.connections.append(conn)
                    self.values[len(self.connections)] = []
            except socket.timeout:
                pass

            for idx, conn in enumerate(self.connections):
                data = conn.recv(1024)
                if data:
                    now = time.time()
                    self.values[idx + 1][now] = int(data)
                    self.print(str(idx + 1) + ":" + str(int(data)))
                    # generic answer for each client
                    conn.sendall('ok'.encode())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print('Closing Server')
        self.stop = True
        for conn in self.connections:
            conn.__exit__(self, exc_type, exc_val, exc_tb)
        self.socket.__exit__(self, exc_type, exc_val, exc_tb)

    def send(self, msg):
        # self.values[0] = msg
        # send to serial com instead of printing
        print(msg)
        pass

    def print(self, msg):
        if self.print_debug:
            print(msg)


class Client:

    def __enter__(self):
        self.socket.__enter__()
        self.socket.connect((self.server_ip, self.server_port))
        return self

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        print('Verbindungsaubau zu: ' + str(self.server_ip) + ':' + str(self.server_port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.__exit__(exc_type, exc_val, exc_tb)

    def send(self, msg):
        self.socket.sendall(str(msg).encode())
        return self.socket.recv(1024) == b'ok'


def init_network(is_server: bool, server_ip: str, server_port: int):
    if is_server:
        return Server(server_ip, server_port, print_debug=True)
    else:
        return Client(server_ip, server_port)


