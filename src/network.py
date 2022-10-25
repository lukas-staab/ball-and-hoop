import select
import threading
import time
import socket
import datetime
from threading import Thread

import scipy.io
import yaml

from src.serial import SerialCom


class Server(Thread):
    def __init__(self, server_ip, server_port, print_debug=False, use_serial=False):
        super().__init__()
        self.daemon = True  # kill it with parent
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets = []
        self.interrupt = threading.Event()
        self.print_debug = print_debug
        self.serial = SerialCom(verbose=print_debug, use_serial=use_serial)
        self.values = {'localhost': {'angle': [], 'time': []}}
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
            while not self.interrupt.is_set():
                self.print('Checking for new Connection')
                # sort sockets by states
                readable, writable, errored = select.select(self.sockets, [], [])
                for s in readable:
                    if s is self.server:
                        # s is the server, so there is a new connection
                        client_socket, address = self.server.accept()
                        client_socket.__enter__()
                        self.values[addr(client_socket)] = {'angle': [], 'time': []}
                        self.sockets.append(client_socket)
                        print("Connection from: " + str(address))
                    else:
                        # s is a client socket, so there is data
                        data = s.recv(1024)
                        if data:
                            self.print(str(addr(s)) + ":" + str(float(data)))
                            self.values[addr(s)]['angle'].append(float(data))
                            self.values[addr(s)]['time'].append(now())
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
            self.stop()

    def stop(self):
        self.print('Interrupt received. Saving measured values to ./storage/result ...')
        scipy.io.savemat('storage/result.mat', {'pi_result': self.values})
        yaml.dump(self.values, open('storage/result.yml', 'w'))
        self.print(self.values.keys())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.print('Closing Server')
        self.interrupt.set()
        self.stop()
        for s in self.sockets:
            s.close()

    def send(self, val):
        # make sure to have a non-negative integer val with  0 <= val < 360
        val = (int(val) + 360) % 360
        # save value history for later
        self.values['localhost']['angle'].append(val)
        self.values['localhost']['time'].append(now())
        # TODO: do not only send the server values but a average or so
        self.serial.write(val)
        pass

    def print(self, msg):
        """ Helper method which suppresses debug output if not wanted """
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
        print("Sending: " + str(msg))
        self.socket.sendall(str(msg).encode())
        return self.socket.recv(1024) == b'ok'


def init_network(is_server: bool, server_ip: str, server_port: int, use_serial: bool = True):
    if is_server:
        return Server(server_ip, server_port, print_debug=True, use_serial=use_serial)
    else:
        return Client(server_ip, server_port)


def addr(s: socket.socket):
    return 's' + str(s.getpeername()[1])


def now():
    return int((datetime.datetime.utcnow().timestamp() % 100) * 1_000_000)
