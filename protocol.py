import math

class Protocol:

    def __init__(self):
        self.packet_id = None

    def parse_packet(self, data):
        raise NotImplementedError

class Protocol_2016(Protocol):

    def __init__(self):
        super().__init__()

        self.did_request_time = False
        self.packet_id = None

        self.PACKET_HEADER = 0x01

        self.MODE_MASK = 0x03
        self.MODE_TEST = 0x01
        self.MODE_AUTO = 0x02
        self.MODE_TELEOP = 0x00

        self.ENABLED = 0x40
        self.FMS_ATTACHED = 0x08
        self.E_STOP = 0x80
        self.ROBOT_CODE = 0x20

        self.REQUEST_REBOOT = 0x08
        self.REQUEST_NORMAL = 0x80
        self.REQUEST_CONNECT = 0x00
        self.REQUEST_RESTARTCODE = 0x04

        self.REQUEST_TIMEDATA = 0x01

        self.STATION_RED_1 = 0x00
        self.STATION_RED_2 = 0x01
        self.STATION_RED_3 = 0x02
        self.STATION_BLUE_1 = 0x03
        self.STATION_BLUE_2 = 0x04
        self.STATION_BLUE_3 = 0x05

        self.JOYSTICK_HEADER = 0x0c
        

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

    def parse_joy_data(self, data):
        joy_list = []
        while len(data) > 0:
            joy_size = data[0]
            if data[1] is not self.JOYSTICK_HEADER:
                raise ValueError("Invalid joystick packet")
            joy_axes_data = data[2:]
            joy_num_axes = joy_axes_data[0]
            joy_axes_values = [(-1*(x&0x80) + (x&0x7F))/0x7F for x in joy_axes_data[1:joy_num_axes+1]]

            joy_button_data = joy_axes_data[joy_num_axes+1:]
            joy_num_buttons = joy_button_data[0]
            joy_button_flags = (joy_button_data[1] << 8) + joy_button_data[2]

            joy_button_values = [False] * joy_num_buttons
            for i in range(joy_num_buttons):
                joy_button_values[i] = int(math.pow(2, i)) & joy_button_flags > 0

            joy_hat_data = joy_button_data[3:]
            joy_num_hats = joy_hat_data[0]
            joy_hat_values = [0] * joy_num_hats
            for i in range(joy_num_hats):
                joy_hat_values[i] = (joy_hat_data[1 + 2*i] << 8) + joy_hat_data[2 + 2*i]


            assert(joy_size == 2 + 3 + (1 + len(joy_axes_values)) + (1 + 2 * len(joy_hat_values)))

            data = data[joy_size:]

            joy_list.append({"axes":joy_axes_values, "buttons":joy_button_values, "hats":joy_hat_values})

        return joy_list


    
    def parse_DS_packet(self, data):
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
        station_data = self.parse_station_code(station_code)

        self.packet_id = packet_id

        joy_data = []

        if len(extradata) > 0:
            if self.did_request_time:
                #self.parse_time_data(extradata)
                pass
            else:
                joy_data = self.parse_joy_data(extradata)

        return (control_data, request, station_data, joy_data)
    
    def generate_control_code(self, robot_state):
        if robot_state.emergency_stopped:
            return self.E_STOP
        else:
            return 0x00
    
    def generate_status_code(self, robot_state):
        if robot_state.robot_code_running:
            return self.ROBOT_CODE
        else:
            return 0x00
    
    def generate_voltage_data(self, robot_state):
        fracpart, wholepart = math.modf(robot_state.robot_voltage)
        wholepart = int(wholepart)
        fracpart = int(fracpart * 255)

        if wholepart > 255 or wholepart < 0:
            wholepart = 255
        if fracpart > 254 or fracpart < 0:
            fracpart = 254
        
        return (wholepart, fracpart)

    def generate_request_data(self):
        if self.did_request_time:
            return self.REQUEST_TIMEDATA
        else:
            return 0x00

    def generate_robot_packet(self, robot_state, packet_mode):
        packet = [0] * 8
        # Don't know what the first 3 bytes represent, so leave them as 0x00
        packet[0:3] = [0x00] * 3

        packet[3] = self.generate_control_code(robot_state)
        packet[4] = self.generate_status_code(robot_state)
        packet[5:7] = self.generate_voltage_data(robot_state)
        packet[7] = self.generate_request_data() # request current time & date

        if packet_mode is "CAN_INFO":
            pass
        elif packet_mode is "CPU_INFO":
            pass
        elif packet_mode is "RAM_INFO":
            pass
        elif packet_mode is "DISK_INFO":
            pass

        return bytearray(packet)

            