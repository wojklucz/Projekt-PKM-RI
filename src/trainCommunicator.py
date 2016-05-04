import socket
import binascii

class TrainCommunicator(object):
    def __init__(self):
        self.connection = None

    def send_data(self,msg):
        assert isinstance(self.connection,socket.socket)
        print "Sending: " + str(msg)
        self.connection.send(binascii.unhexlify(msg))
        response = self.connection.recv(64)
        print "Recieved: " + binascii.hexlify(response)

    def connect(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip,port))
        data = "fffef101f0"
        self.send_data(data)

    def mushroom_stop(self):
        cmd = "fffe8080"
        self.send_data(cmd)

if __name__ == '__main__':
    kom = TrainCommunicator()
    kom.connect('192.168.0.200', 5550)
    kom.mushroom_stop()
