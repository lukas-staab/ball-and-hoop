import select
import time
import socket
import datetime
from threading import Thread

import scipy.io

from src.serial import SerialCom


class Server(Thread):
    def __init__(self, server_ip, server_port, print_debug=False):
        super().__init__()
        self.daemon = True  # kill it with parent
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets = []
        self.stop = False
        self.stopped = False
        self.print_debug = print_debug
        # self.serial = SerialCom()
        self.values = {'localhost': {}}
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
            while not self.stop:
                readable, writable, errored = select.select(self.sockets, [], [])
                for s in readable:
                    if s is self.server:
                        # s is the server
                        client_socket, address = self.server.accept()
                        client_socket.__enter__()
                        self.values[addr(client_socket)] = {}
                        self.sockets.append(client_socket)
                        print("Connection from: " + str(address))
                    else:
                        # s is a client socket
                        data = s.recv(1024)
                        if data:
                            self.print(addr(s) + ":" + str(float(data)))
                            self.values[addr(s)][now()] = float(data)
                            # generic answer for each client, message confirmed
                            s.sendall('ok'.encode())
                        else:
                            s.close()
                            self.sockets.remove(s)
        except SystemExit:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            self.stopped = True
            scipy.io.savemat('storage/result.mat', {'pi_result': self.values})
            self.print(self.values.keys())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print('Closing Server')
        self.stop = True
        while self.stopped is not True:
            time.sleep(0.1)
        for s in self.sockets:
            s.close()

    def send(self, msg):
        # send to serial com instead of printing
        self.values['localhost'][now()] = float(msg)
        print("localhost: " + str(float(msg)))
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


def addr(s: socket.socket):
    return s.getpeername()[1]


def now():
    return datetime.datetime.utcnow().timestamp()
