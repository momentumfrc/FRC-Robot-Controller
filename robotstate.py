class RobotState:

    def __init__(self):
        self.control_mode = "TELEOP"
        self.control_enabled = False
        self.fms_attached = False

        self.emergency_stopped = False
        self.robot_code_running = True
        self.robot_voltage = 0.0

        self.alliance_color = "RED"
        self.alliance_station = 1
    
    def update_controldata(self, data):
        self.control_mode, self.control_enabled, self.fms_attached, self.emergency_stopped = data

    def update_stationdata(self, data):
        self.alliance_color, self.alliance_station = data