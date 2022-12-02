import serial


class SerialCom:
    """
    Organizes the serial communication to the dspace card

    :param verbose: flag if more output should be given, defaults to false
    :param com: the com port to use, on linux a file, defaults to '/dev/serial0' (rpi v4)
    :param baud: the baud rate
    :param active: flag if serial connection should be established, usefull for mockup usage, defaults to True
    :param message_bytes: the length in bytes of the send message per given data, defaults to 2
    :param send_mode: the send mode (not yet implemented)
    :param send_errors: flag if errors should be transmitted, defaults to False (not yet implemented)
    """
    def __init__(self, verbose=False, com='/dev/serial0', baud=9600,
                 active=True, message_bytes=2, send_mode=1, send_errors=False):
        self.message_bytes = message_bytes
        self.active = active
        if active:
            self.serial = serial.Serial(com, baudrate=baud)
        self.verbose = verbose

    def write(self, angle: int):
        """
        The method to call to write an int over the serial line

        :param angle: the angle in int
        """
        # transform angle to byte representation
        angel_byte = angle.to_bytes(self.message_bytes, byteorder='big')
        # if there is no serial port installed (e.g. on the local machine) do not try to send it
        if self.active:
            self.serial.write(angel_byte)
        # debug output to console
        if self.verbose:
            print("Serial: " + str(angle) + " | hex rep: " + str(angel_byte))
