
import serial
import time

#port = "/dev/ttyAMA0"  # Raspberry Pi 2
#port = "/dev/ttyS0"    # Raspberry Pi 3
port = "/dev/serial0"

ser = serial.Serial(port, baudrate = 9600)
print("starting")
value = 1
while True:
    time.sleep(.1)
    ser.write(value.to_bytes(1, byteorder='big'))
    print('Send: ' + str(value))
    value = (value +1) % 256
    nbChars = ser.inWaiting()
    if nbChars > 0:
        data = ser.read(nbChars)
        data = int(data)
        print(data)
