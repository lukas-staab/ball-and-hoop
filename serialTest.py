
import serial
import time

#port = "/dev/ttyAMA0"  # Raspberry Pi 2
#port = "/dev/ttyS0"    # Raspberry Pi 3
port = "/dev/serial0"

ser = serial.Serial(port, baudrate = 1200)
print("starting")
value = 1
while True:
    time.sleep(1)
    bArray = ord("A")
    ser.write(value)
    print('Send: ' + str(value))
    value += 1
    nbChars = ser.inWaiting()
    if nbChars > 0:
        data = ser.read(nbChars)
        print(data)
