import select
import threading
import socket
import datetime
from threading import Thread

import scipy.io
import yaml

from src.serial import SerialCom


class NetworkInterface():
    def __init__(self, send_errors: bool = True, precision: int = 360, message_bytes: int = 2):
        self.precision = int(precision)
        self.send_errors = send_errors
        self.message_bytes = message_bytes

        # 10 values are reserved for Errors
        self.max_precision = 2 ** (8 * message_bytes)
        if precision + 10 > self.max_precision:
            raise ArithmeticError('Not enough message_bytes to fulfill precision')

        self.NOT_FOUND = self.max_precision - 1
        self.WRONG_ORDER = self.max_precision - 2
        self.ERROR = self.max_precision - 3
        self.LOST_CONNECTION = self.max_precision - 4

    def preprocess_message(self, data:float ) -> (int, bool):
        if data >= self.max_precision - 10:
            # this is an error code
            if self.send_errors:
                return data, True
        # rescale data, if needed
        if self.precision != 360:
            data = int(data / 360.0 * self.precision)
        # shift negative values
        return int((data + self.precision) % self.precision), False

    def send(self, val):
        raise Exception('Has to be overwritten by child class')


class Server(Thread, NetworkInterface):
    def __init__(self, server_ip, server_port, serial, print_debug=False, **kwargs):
        NetworkInterface.__init__(self, **kwargs)
        Thread.__init__(self, daemon=True)  # init Thread, deamon=True: kill it if parent tread is killed
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets = []
        self.interrupt = threading.Event()
        self.write_value_lock = threading.Lock()
        self.print_debug = print_debug
        self.serial = SerialCom(verbose=print_debug, message_bytes=self.message_bytes, **serial)
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
                            # generic answer for each client, message confirmed
                            s.sendall('ok'.encode())
                            # save values for later
                            data, is_error = self.preprocess_message(data)
                            self.save_values(data, addr(s), is_error=is_error)
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

    def save_values(self, data, source, is_error:bool):
        with self.write_value_lock:
            self.values[source]['time'].append(now())
            if is_error:
                self.values[source]['error'].append(data - self.max_precision + 10)
                self.values[source]['angle'].append(self.values[source]['angle'][-1])
            else:
                self.values[source]['angle'].append(int(data))
                self.values[source]['error'].append(0)

    def latest_values(self):
        with self.write_value_lock:
            return []
    def send(self, val):
        val, is_error = self.preprocess_message(val)
        if not is_error or (is_error and self.send_errors):
            # save value history for later
            self.save_values(val, 'localhost', is_error=is_error)
            vals = self.latest_values()
            self.serial.write(vals)

    def print(self, msg):
        """ Helper method which suppresses debug output if not configured """
        if self.print_debug:
            print(msg)


class Client(NetworkInterface):

    def __enter__(self):
        self.socket.__enter__()
        self.socket.connect((self.server_ip, self.server_port))
        return self

    def __init__(self, server_ip, server_port, **kwargs):
        NetworkInterface.__init__(self, **kwargs)
        self.server_ip = server_ip
        self.server_port = server_port
        print('Verbindungsaubau zu: ' + str(self.server_ip) + ':' + str(self.server_port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.__exit__(exc_type, exc_val, exc_tb)

    def send(self, val):
        val, is_error = self.preprocess_message(val)
        if not is_error or (is_error and self.send_errors):
            print("Sending: " + str(val))
            self.socket.sendall(str(val).encode())
            return self.socket.recv(1024) == b'ok'
        return False


def init_network(is_server: bool, server_ip: str, server_port: int = 9999, **kwargs) -> NetworkInterface:
    """ This function is a wrapper for dynamic construction of the Client or Server Class depending on the config
    file, some parameters are only relevant in a server context """
    if is_server:
        return Server(server_ip, server_port, **kwargs)
    else:
        return Client(server_ip, server_port, **kwargs)


def addr(s: socket.socket):
    return 's' + str(s.getpeername()[1])


def now():
    return int((datetime.datetime.now().timestamp() % 10_000) * 1_000)
