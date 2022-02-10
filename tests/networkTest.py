# construct the argument parse and parse the arguments
import argparse
import socket
import numpy
from datetime import datetime
from tabulate import tabulate

ap = argparse.ArgumentParser()
# ---------------------------------------------------
ap.add_argument("-i", "--server-ip", type=str, default="127.0.0.1",
                help="The Server IP address to connect to, do not use together with -s")
ap.add_argument("-s", "--server", action='store_true', help="Use to start in server mode")  # server flag
ap.add_argument("-p", "--port", type=int, default=9999, help="The port to listen at / to send to")
# ---------------------------------------------------
args = vars(ap.parse_args())

if args['server']:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args['server_ip'], args['port']))
        print('Startup server. Press CRTL+C to stop.')
        s.listen(1)
        try:
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        # send answer
                        now = str(datetime.utcnow()).encode()
                        conn.sendall(now)
        except KeyboardInterrupt:
            print('Stopping Server')
            pass
else:
    diffs = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args['server_ip'], args['port']))
        for i in range(1, 10):
            now = datetime.utcnow()
            s.sendall(str(now).encode())
            receivedTime = s.recv(1024)
            receivedNow = datetime.strptime(receivedTime.decode(), '%Y-%m-%d %H:%M:%S.%f')
            diffs.append(receivedNow - now)
    print(tabulate({'The delays:': diffs}, headers='keys'))
    print('--------------')
    print(tabulate({
        'The Min: ': [numpy.min(diffs)],
        'The Average: ': [numpy.mean(diffs)],
        'The Max: ': [numpy.max(diffs)],
    }, headers='keys'))
