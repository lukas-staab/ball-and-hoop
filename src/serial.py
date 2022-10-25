import serial


class SerialCom:
    def __init__(self, port='/dev/serial0', baud=9600):
        self.serial = serial.Serial(port, baudrate=baud)

    def write(self, angle, rad=0):
        angel_byte = angle.to_bytes(2, byteorder='big')
        # rad_byte = rad.to_bytes(2, byteorder='big')
        self.serial.write(angel_byte)
        # self.serial.write(rad_byte)
