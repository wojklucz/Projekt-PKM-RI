import socket
import binascii

from time import sleep

class TrainCommunicator(object):
    """Object comunicating with the trains
        Attributes:
            connection (socket): Allows connection with the trains

        """
    def __init__(self):
        self.connection = None     #Placeholder for socket

    def send_data(self,msg):
        """Sends a message with prepended header and appended checksum

              Args:
                  msg: message prepared to send

              Returns:
                  None

              """
        assert isinstance(self.connection,socket.socket)    #check if socket is set
        xor = self.calculate_checksum(msg)                  #calculate cheksum byte
        print "Sending: " + str(msg) + " XOR: " + str(xor)
        msg += xor                                     #append XOR byte
        msg = "fffe" + msg                             #add header
        msg = binascii.unhexlify(msg)                  #convert to raw data
        self.connection.send(msg)                      #send it
        response = self.connection.recv(64)            #recieve response
        response = binascii.hexlify(response)          #covert to readable
        response = response[4:]                        #strip header
        xor = response[-2:]                            #get cheksum
        response = response [:-2]                      #strip chekscum
        print "Recieved: " + response + " XOR: " + str(xor)
        if self.calculate_checksum(response) != xor:   #check if cheksum ok
            raise Exception("Communication error: BAD CHEKSUM")
        else:
            print "Cheksum OK"

    def connect(self, ip, port):
        """Connect with the command station

              Args:
                  ip: Command station ip
                  port: Command station port.

              Returns:
                  None
              """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip,port))
        data = "f101"
        self.send_data(data)

    def calculate_checksum(self,msg):
        """Calculates the checksum for the message

              Args:
                  msg(str): message to send

              Returns:
                  None

              """
        s = msg
        byte_list = []
        while s:  # split string into bytes
            byte_list.append(int(s[:2], 16))
            s = s[2:]
        for i in range(1, len(byte_list)):
            if i == 1:
                xor = byte_list[i - 1] ^ byte_list[i]   # xor first with second
            else:
                xor = xor ^ byte_list[i]                # xor previous xor with next byte
        if len(byte_list) == 1:
            xor = byte_list[0]
        if  xor < 16:
            xor = hex(xor)[2:]  # decimal to hex, remove 0x
            xor = "0" + xor
        else:
            xor = hex(xor)[2:]  # decimal to hex, remove 0x
        return xor

    #command section - function names explain what the appropriate codes do
    def acknowledgement_response(self):
        cmd = "20"
        self.send_data(cmd)

    def resume_operations_request(self):
        cmd = "2181"
        self.send_data(cmd)

    def emergency_off(self):
        cmd = "2180"
        self.send_data(cmd)

    def emergency_stop(self):
        cmd = "80"
        self.send_data(cmd)

    def command_station_software_version_request(self):
        cmd = "2121"
        self.send_data(cmd)

    def set_speed(self,loco,speed):
        """Sets speed for specified locomotive

                      Args:
                          loco(int): id of locomotive to set speed
                          speed(str): one of choices
                          "przod":foward,
                          "tyl":backward,
                          "stop":0

                      Returns:
                          None

                      """
        predkosci = {"przod":"30","stop":"00","tyl":"B0"}
        if loco < 16:
            loco = "0" + hex(loco)[2:]
        else:
            loco = hex(loco)[2:]
        print loco
        print "Speed: " + speed
        cmd = "e41300" + loco + predkosci[speed]
        self.send_data(cmd)

    def add_a_locomotive_to_a_multi_unit_request(self, loco):
        if loco < 16:
            loco = "0" + hex(loco)[2:]
        else:
            loco = hex(loco)[2:]
        cmd = "440000" + loco + "03"   #ustalic XOR, MTR=1-99
        self.send_data(cmd)                                 #R=0 jesli kierunek sie zgadza, R=1 jesli jest przeciwny

    # TODO: Implement this methods if needed
    # def emergency_stop_a_locomotive(self, address):
    #     cmd = "92000" + address + XOR     #ustalic XOR
    #     self.send_data(cmd)
    #
    # def register_mode_read_request(self):
    #     cmd = "2211 R XOR"      #ustalic R 1-8
    #     self.send_data(cmd)
    #
    # def direct_mode_cv_read_request(self):
    #     cmd = "2215 CV XOR"         #ustalic CV 1-256
    #     self.send_data(cmd)
    #
    # def paged_mode_read_request(self):
    #     cmd = "2214 CV XOR"         #ustalic CV 1-256
    #     self.send_data(cmd)
    #
    # def request_for_service_mode_result(self):
    #     cmd = "211031"
    #     self.send_data(cmd)
    #
    # def register_mode_write_request(self):
    #     cmd = "2312 R Data XOR"         #ustalic R, Data, XOR
    #     self.send_data(cmd)
    #
    # def direct_mode_cv_write_request(self):
    #     cmd = "2316 cv Data XOR"         #ustalic cv, Data, XOR
    #     self.send_data(cmd)
    #
    # def paged_mode_write_request(self):
    #     cmd = "2317 cv Data XOR"         #ustalic cv, Data, XOR
    #     self.send_data(cmd)
    #
    #
    # def remove_a_locomotive_from_a_multi_unit_request(self, address):
    #     cmd = "e442000" + address + MTR + XOR
    #     self.send_data(cmd)
    #
    # def address_inquiry_member_of_a_multi_unit_request(self, address, R):
    #     cmd = "e401 + R" + MTR+ "000" + address + XOR
    #     self.send_data(cmd)
    #
    # def address_inquiry_multi_unit_request(self, R):
    #     cmd = "e203 + R" + MTR + XOR
    #     self.send_data(cmd)
    #
    # def address_inquiry_locomotive_at_command_station_stack_request(self, address, R):
    #     cmd = "e305 + R" + "000" + address + XOR
    #     self.send_data(cmd)
    #
    # def delete_locomotive_from_command_station_stack_request(self, address):
    #     cmd = "e344000" + address + XOR
    #     self.send_data(cmd)
    #
    # def command_station_status_request(self):
    #     cmd = "212405"
    #     self.send_data(cmd)
    #
    # def set_command_station_power_up_mode(self, M):
    #     cmd = "2222" + M + XOR      #M = 0 wlaczenie manualne lokomotyw bez podania predkosci
    #     self.send_data(cmd)             #M = 1 wlaczenie automatyczne lokomotyw z ostatnimi predkosciami
    #
    # def accessory_decoder_information_request(self):
    #     cmd = "42 address 80 + N XOR"   #ustalic
    #     self.send_data(cmd)
    #
    # def accessory_decoder_operation_request(self):
    #     cmd = "52 address 80 + DBBD XOR"   #ustalic
    #     self.send_data(cmd)
    #
    # def locomotive_information_requests(self, address):
    #     cmd = "e300000" + address + XOR     #ustalic XOR
    #     self.send_data(cmd)
    #
    # def function_status_request(self, number):
    #     cmd = "e307000" + number + XOR     #ustalic XOR
    #     self.send_data(cmd)
    #
    # def locomotive_speed_and_direction_operations(self, address):
    #     cmd = "e410000" + address + RV + XOR     #ustalic RV, XOR
    #     self.send_data(cmd)

if __name__ == '__main__':
    #short test moving train 2 back and forth
    kom = TrainCommunicator()
    kom.connect('192.168.0.200', 5550)
    kom.set_speed(2,"tyl")
    sleep(5)
    kom.set_speed(2,"przod")
    sleep(5)
    kom.set_speed(2,"stop")
