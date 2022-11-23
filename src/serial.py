import serial


class SerialCom:
    def __init__(self, verbose=False, com='/dev/serial0', baud=9600,
                 active=True, message_bytes=2, send_mode=1, send_errors=False):
        self.message_bytes = message_bytes
        self.active = active
        if active:
            self.serial = serial.Serial(com, baudrate=baud)
        self.verbose = verbose

    def write(self, angle: int):
        # transform angle to byte representation
        angel_byte = angle.to_bytes(self.message_bytes, byteorder='big')
        # if there is no serial port installed (e.g. on the local machine) do not try to send it
        if self.active:
            self.serial.write(angel_byte)
        # debug output to console
        if self.verbose:
            print("Serial: " + str(angle) + " | hex rep: " + str(angel_byte))
