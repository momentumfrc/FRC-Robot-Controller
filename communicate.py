import socket
import protocol

class Communicator:
    def __init__(self, protocol, listen_ip="0.0.0.0", listen_port=1110):
        self.protocol = protocol
        self.listen_ip = listen_ip
        self.listen_port = listen_port

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind((self.listen_ip, self.listen_port))

    def recieve_data(self):
        data, _ = self.listen_socket.recvfrom(1024)
        self.protocol.parse_packet(data)
        

if __name__ == "__main__":
    comm = Communicator(protocol.Protocol_2016(), "127.0.0.1")
    while True:
        comm.recieve_data()