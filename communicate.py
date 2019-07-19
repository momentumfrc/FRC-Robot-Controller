import socket
import protocol
import robotstate
import watchdog

class Communicator:
    def __init__(self, protocol, listen_ip="0.0.0.0", listen_port=1110):
        self.protocol = protocol
        self.listen_ip = listen_ip
        self.listen_port = listen_port

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind((self.listen_ip, self.listen_port))

        self.robot_state = robotstate.RobotState()

        self.connection_watchdog = watchdog.Watchdog(50, 1000, self.connection_timeout)
    
    def connection_timeout(self):
        print("No coms")
        self.robot_state.control_enabled = False

    def connect_ds(self, ds_ip, ds_port=1150):
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ds_ip = ds_ip
        self.ds_port = ds_port

    def communicate(self):
        data, address = self.listen_socket.recvfrom(1024)
        ds_packet =  self.protocol.parse_DS_packet(data)
        if ds_packet is None:
            return
        control_data, request, station_data, joy_data = ds_packet

        self.connection_watchdog.reset()

        if len(joy_data) > 0:
            print(joy_data[0]["axes"])

        self.robot_state.update_controldata(control_data)
        self.robot_state.update_stationdata(station_data)
        
        if request == "CONNECT":
            self.connect_ds(address)
        
        if self.send_socket is not None:
            reply_data = self.protocol.generate_robot_packet(self.robot_state, "NORMAL")
            self.send_socket.sendto(reply_data, (self.ds_ip[0], self.ds_port))
        

if __name__ == "__main__":
    comm = Communicator(protocol.Protocol_2016(), "127.0.0.1")
    while True:
        comm.communicate()