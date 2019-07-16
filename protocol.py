class Protocol:

    def __init__(self):
        self.packet_id = None

    def parse_packet(self, data):
        raise NotImplementedError

class Protocol_2016(Protocol):

    def __init__(self):
        super().__init__()

        self.PACKET_HEADER = 0x01

        self.MODE_MASK = 0x03
        self.MODE_TEST = 0x01
        self.MODE_AUTO = 0x02
        self.MODE_TELEOP = 0x00

        self.ENABLED = 0x40
        self.FMS_ATTACHED = 0x08
        self.E_STOP = 0x80

        self.REQUEST_REBOOT = 0x08
        self.REQUEST_NORMAL = 0x80
        self.REQUEST_CONNECT = 0x00
        self.REQUEST_RESTARTCODE = 0x04

        self.STATION_RED_1 = 0x00
        self.STATION_RED_2 = 0x01
        self.STATION_RED_3 = 0x02
        self.STATION_BLUE_1 = 0x03
        self.STATION_BLUE_2 = 0x04
        self.STATION_BLUE_3 = 0x05
        

    def parse_control_code(self, control_code):
        modebits = control_code & self.MODE_MASK
        if modebits == self.MODE_TEST:
            mode = "TEST"
        elif modebits == self.MODE_AUTO:
            mode = "AUTO"
        elif modebits == self.MODE_TELEOP:
            mode = "TELEOP"
        else:
            raise ValueError("Invalid packet: bad mode")

        enabled = control_code & self.ENABLED > 0
        fms_attached = control_code & self.FMS_ATTACHED > 0
        e_stopped = control_code & self.E_STOP > 0

        return (mode, enabled, fms_attached, e_stopped)

    def parse_request_code(self, request_code):
        if request_code == self.REQUEST_NORMAL:
            return "NORMAL"
        elif request_code == self.REQUEST_REBOOT:
            return "REBOOT"
        elif request_code == self.REQUEST_RESTARTCODE:
            return "RESTARTCODE"
        elif request_code == self.REQUEST_CONNECT:
            return "CONNECT"
        else:
            raise ValueError("Invalid packet: bad request code")
        
    def parse_station_code(self, station_code):
        if station_code == self.STATION_RED_1:
            return ("RED", 1)
        elif station_code == self.STATION_RED_2:
            return ("RED", 2)
        elif station_code == self.STATION_RED_3:
            return ("RED", 3)
        elif station_code == self.STATION_BLUE_1:
            return ("BLUE", 1)
        elif station_code == self.STATION_BLUE_2:
            return ("BLUE", 2)
        elif station_code == self.STATION_BLUE_3:
            return ("BLUE", 3)
    
    def parse_packet(self, data):
        packet_id = (data[0] << 8) | data[1]
        header = data[2]
        control_code = data[3]
        request_code = data[4]
        station_code = data[5]

        extradata = data[6:]

        if header is not self.PACKET_HEADER:
            return
        if self.packet_id is not None and self.packet_id >= packet_id:
            return

        control_data = self.parse_control_code(control_code)
        request = self.parse_request_code(request_code)
        station = self.parse_station_code(station_code)

        self.packet_id = packet_id
        print(control_data, request, station)
        

            