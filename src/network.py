import select
import threading
import socket
import datetime
from threading import Thread

import scipy.io
import yaml

from src.serial import SerialCom


class NetworkInterface():
    """
    Abstracts the send method, and how to do the preprocessing of the data to send

    :param send_errors: flag if errors should be sent or only logged
    :param precision: the base degree of the angle, defaults to 360
    :type precision: int
    :param message_bytes: how many bytes the data should have in ethernet and serial, 2^(8*message_bytes) has to be bigger than precission, defaults to 2
    :param kwargs: a catch-all argument, so constructor can be filled by config

    :ivar max_precision: equals 2^(8 * message_bytes), the highest 10 values are reserved for error codes
    :ivar NOT_FOUND: max_precision - 1, an error code for a not found ball
    :ivar WRONG_ORDER: max_precision - 2, an error code for a failed race condition
    :ivar ERROR: max_precision - 3, an error code, for a general error
    :ivar LOST_CONNECTION: max_precision - 4, an error code, for a lost camera-pi
    """
    def __init__(self, send_errors: bool = True, precision: int = 360, message_bytes: int = 2, **kwargs):

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

    def preprocess_message(self, data: float) -> (int, bool):
        """
        Rebases the data from 360 degree to the given precision.

        :param data: the date which should be converted
        :type data: float
        :return: the angle in the new base cast to int and if this is an error
        :rtype: (int, bool)
        """
        if data >= self.max_precision - 10:
            # this is an error code
            if self.send_errors:
                return int(data), True
        # rescale data, if needed
        if self.precision != 360:
            data = int(data / 360.0 * self.precision)
        # shift negative values
        return int((data + self.precision) % self.precision), False

    def send(self, val):
        """
        A placeholder which will be overwritten by its parents

        :param val: the data
        """
        raise Exception('Has to be overwritten by child class')


class Server(Thread, NetworkInterface):
    """
    The server class. Manages the incoming connections from clients, pipes data to the serial port and is logging
    the values for a later plotting usage

    :param server_ip: the ip of the server (has to be localhost)
    :param server_port: the port we are waiting for connections
    :param serial: the configuration for the serial class
    :param print_debug: a flag if debug output should be printed or discarded
    :param kwargs: a catch-all parameter for additional config given

    :ivar serial: A object of the :py:class:`SerialCom`
    """
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
        self.values = {}
        self.host_map = {'local': socket.gethostname()}
        print('Init Server')

    def __enter__(self):
        """
        Starts the network server thread and configures the server ports

        :return: self
        :rtype: NetworkInterface
        """
        self.server.__enter__()
        self.server.bind((self.server_ip, self.server_port))
        self.server.settimeout(5)
        self.server.listen(2)
        self.start()
        return self

    def run(self) -> None:
        """
        Runs the network server. This method is started in a separate thread
        It iterates through all connection sockets, including the server, watching for new data or connections.
        The first given data is the hostname, so a reconnect with the same hostname is possible server vice

        """
        self.print('Server is running')
        self.sockets.append(self.server)
        try:
            while not self.interrupt.is_set():
                self.print('Checking for new Connection')
                # sort sockets by states
                readable, writable, errored = select.select(self.sockets, [], [])
                # iterate over all sockets with new readable information
                for s in readable:
                    # check if this socket is the server
                    if s is self.server:
                        # s is the server, so there is a new connection
                        client_socket, address = self.server.accept()
                        client_socket.__enter__()
                        self.sockets.append(client_socket)
                        print("Connection from: " + str(address))
                    else:
                        # s is a client socket, so there is data
                        data = s.recv(1024)
                        if data:
                            if addr(s) not in self.host_map:
                                # first data sent is his hostname - save for remapping the connection
                                self.host_map[addr(s)] = data.decode()
                            else:
                                # save values for later
                                data, is_error = self.preprocess_message(int(data.decode()))
                                self.save_values(data, addr(s), is_error=is_error)
                            # self.print(str(addr(s)) + ":" + str(float(data)))
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
        """
        Saves the data which was sent in a result.mat and result.yml file

        :return:
        """
        self.print('Interrupt received. Saving measured values to ./storage/result ...')
        scipy.io.savemat('storage/result.mat', {'pi_result': self.values})
        yaml.dump(self.values, open('storage/result.yml', 'w'))
        # self.print(self.values.keys())

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the server. Parameters are typical parameters for error detection

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.print('Closing Server')
        self.interrupt.set()
        self.stop()
        for s in self.sockets:
            s.close()

    def save_values(self, data, address, is_error:bool):
        """
        Saves the value (or error) in an value array, together with the time.
        The hostname is used as a a top level key.

        :param data: the data
        :param address: connection address, where the hostname can be deducted from
        :param is_error: a flag if this data is an error code, so we do nat have to check here
        :return:
        """
        hostname = self.host_map[address]
        with self.write_value_lock:
            if hostname not in self.values:
                self.values[hostname] = {'time': [], 'angle': [], 'error': []}
            self.values[hostname]['time'].append(now())
            if is_error:
                self.values[hostname]['error'].append(data - self.max_precision + 10)
                prev_val = 0
                if len(self.values[hostname]['angle']) > 0:
                    prev_val = self.values[hostname]['angle'][-1]
                self.values[hostname]['angle'].append(prev_val)
            else:
                self.values[hostname]['angle'].append(int(data))
                self.values[hostname]['error'].append(0)

    def latest_values(self):
        """
        WIP Gets the latest value

        :return: an empty erray
        """
        with self.write_value_lock:
            return []
    def send(self, val):
        """
        does not send the data to the server, because this is the server allready.
        So it justs saves the data and pipes the data through to the serial interface.
        If you want to send something else then just the hostdata, you need to change this class

        :param val:
        :return:
        """
        val, is_error = self.preprocess_message(val)
        if not is_error or (is_error and self.send_errors):
            # save value history for later
            self.save_values(val, 'local', is_error=is_error)
            # vals = self.latest_values()
            self.serial.write(val)

    def print(self, msg):
        """ Helper method which suppresses debug output if not configured """
        if self.print_debug:
            print(msg)


class Client(NetworkInterface):

    def __enter__(self):
        self.socket.__enter__()
        try:
            self.socket.connect((self.server_ip, self.server_port))
            self.socket.sendall(str(socket.gethostname()).encode())
            if self.socket.recv(1024) == b'ok':
                return self
        except ConnectionRefusedError:
            print("Connection to server refused. Not yet running on this port/ip?")
            exit(1)

    def __init__(self, server_ip, server_port, **kwargs):
        NetworkInterface.__init__(self, **kwargs)
        self.server_ip = server_ip
        self.server_port = server_port
        print('Connecting to: ' + str(self.server_ip) + ':' + str(self.server_port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.__exit__(exc_type, exc_val, exc_tb)

    def send(self, val):
        """
        Sends the data to the server

        :param val: the angle or the error
        :return:
        """
        try:
            val, is_error = self.preprocess_message(val)
            if not is_error or (is_error and self.send_errors):
                self.socket.sendall(str(val).encode())
                return self.socket.recv(1024) == b'ok'
            return False
        except ConnectionResetError:
            print('Server wurde beendet')
            exit(1)


def init_network(is_server: bool, server_ip: str, server_port: int = 9999, **kwargs) -> NetworkInterface:
    """
    This function is a wrapper for dynamic construction of the Client or Server Class depending on the config
    file, some parameters are only relevant in a server context
    """
    if is_server:
        return Server(server_ip, server_port, **kwargs)
    else:
        return Client(server_ip, server_port, **kwargs)


def addr(s: socket.socket):
    """
    A helper method to get a unique string per connection

    :param s: the socket
    :return:
    """
    return 's' + str(s.getpeername()[1])


def now():
    """
    A helper method to get an integer value which can be used as a time axis

    :return: a time integer in ms, repeats every 10.000 seconds
    """
    return int((datetime.datetime.now().timestamp() % 10_000) * 1_000)
