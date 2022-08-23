import select
import time
import socket
from threading import Thread

import scipy.io

from src.serial import SerialCom


class Server(Thread):
    def __init__(self, server_ip, server_port, print_debug=False):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets = []
        self.stop = False
        self.stopped = False
        self.print_debug = print_debug
        # self.serial = SerialCom()
        self.values = {0: {}}
        print('Init Server')

    def __enter__(self):
        self.server.__enter__()
        self.server.bind((self.server_ip, self.server_port))
        self.server.settimeout(5)
        self.server.listen(2)
        self.start()
        return self

    def run(self) -> None:
        self.print('Server is running')
        self.sockets.append(self.server)
        try:
            while True:
                readable, writable, errored = select.select(self.sockets, [], [])
                for s in readable:
                    if s is self.sockets:
                        client_socket, address = self.server.accept()
                        self.sockets.append(client_socket)
                        client_socket.__enter__()
                        self.values[s] = {}
                        print("Connection from: " + str(address))
                    else:
                        # this is a client socket
                        data = s.recv(1024)
                        if data:
                            now = time.time()
                            self.values[s][now] = int(data)
                            self.print(str(s) + ":" + str(int(data)))
                            # generic answer for each client
                            s.sendall('ok'.encode())
                        else:
                            s.close()
                            self.sockets.remove(s)
        finally:
            self.stopped = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print('Closing Server')
        self.stop = True
        while self.stopped is not True:
            time.sleep(0.1)
        for s in self.sockets:
            s.__exit__(self, exc_type, exc_val, exc_tb)
        scipy.io.savemat('storage/result.mat', {'pi_result': self.values})

    def send(self, msg):
        # self.values[0] = msg
        # send to serial com instead of printing
        self.values[0][time.time()] = int(msg)
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


