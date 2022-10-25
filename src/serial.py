import serial


class SerialCom:
    def __init__(self, port='/dev/serial0', baud=9600, verbose=False, use_serial=True):
        self.use_serial = use_serial
        if use_serial:
            self.serial = serial.Serial(port, baudrate=baud)
        self.verbose = verbose

    def write(self, angle, byte_amount=2):
        # transform angle to byte representation
        angel_byte = angle.to_bytes(byte_amount, byteorder='big')
        # if there is no serial port installed (e.g. on the local machine) do not try to send it
        if self.use_serial:
            self.serial.write(angel_byte)
        # debug output to console
        if self.verbose:
            print("Serial: " + str(angle) + " | hex rep: " + str(angel_byte))

