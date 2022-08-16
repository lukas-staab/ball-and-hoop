# construct the argument parse and parse the arguments
import argparse
import time

import numpy
from datetime import datetime
from tabulate import tabulate
import repackage
repackage.up()
from src.network import Server, Client

ap = argparse.ArgumentParser()
# ---------------------------------------------------
ap.add_argument("-i", "--server-ip", type=str, default="127.0.0.1",
                help="The Server IP address to connect to, do not use together with -s")
ap.add_argument("-s", "--server", action='store_true', help="Use to start in server mode")  # server flag
ap.add_argument("-p", "--port", type=int, default=9999, help="The port to listen at / to send to")
# ---------------------------------------------------
args = vars(ap.parse_args())

if args['server']:
    with Server(args['server_ip'], args['port']) as server:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
else:
    diffs = []
    print(args['server_ip'])
    with Client(args['server_ip'], args['port']) as c:
        for i in range(1, 10):
            sendTime = datetime.utcnow()
            answer = c.send(str(sendTime).encode())
            receivedTime = datetime.utcnow()
            diffs.append((receivedTime - sendTime).total_seconds() * 1000)
            time.sleep(.01)
    print('Round-Trip-Time (RTT) was measured')
    # print(tabulate({'RTT [ms]:': diffs}, headers='keys'))
    print('--------------')
    print(tabulate({
        'Einheiten': ['ms', 'Hz/"FPS"'],
        'The Min': [numpy.min(diffs), int(1000/numpy.min(diffs))],
        'The Average': [numpy.mean(diffs), int(1000/numpy.mean(diffs))],
        'The Max': [numpy.max(diffs), int(1000/numpy.max(diffs))],
    }, headers='keys'))
