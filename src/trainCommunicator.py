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

    def acknowledgement_response(self):
        cmd = "fffe2020"
        self.send_data(cmd)

    def resume_operations_request(self):
        cmd = "fffe2181a0"
        self.send_data(cmd)

    def emergency_off(self):
        cmd = "fffe2180a1"
        self.send_data(cmd)

    def emergency_stop(self):
        cmd = "fffe8080"
        self.send_data(cmd)

    def emergency_stop_a_locomotive(self, address):
        cmd = "fffe92000" + address + XOR     #ustalic XOR
        self.send_data(cmd)

    def register_mode_read_request(self):
        cmd = "fffe2211 R XOR"      #ustalic R 1-8
        self.send_data(cmd)

    def direct_mode_cv_read_request(self):
        cmd = "fffe2215 CV XOR"         #ustalic CV 1-256
        self.send_data(cmd)

    def paged_mode_read_request(self):
        cmd = "fffe2214 CV XOR"         #ustalic CV 1-256
        self.send_data(cmd)

    def request_for_service_mode_result(self):
        cmd = "fffe211031"
        self.send_data(cmd)

    def register_mode_write_request(self):
        cmd = "fffe2312 R Data XOR"         #ustalic R, Data, XOR
        self.send_data(cmd)

    def direct_mode_cv_write_request(self):
        cmd = "fffe2316 cv Data XOR"         #ustalic cv, Data, XOR
        self.send_data(cmd)

    def paged_mode_write_request(self):
        cmd = "fffe2317 cv Data XOR"         #ustalic cv, Data, XOR
        self.send_data(cmd)

    def command_station_software_version_request(self):
        cmd = "fffe212100"
        self.send_data(cmd)

    def command_station_status_request(self):
        cmd = "fffe212405"
        self.send_data(cmd)

    def set_command_station_power_up_mode(self, M):
        cmd = "fffe2222" + M + XOR      #M = 0 wlaczenie manualne lokomotyw bez podania predkosci
        self.send_data(cmd)             #M = 1 wlaczenie automatyczne lokomotyw z ostatnimi predkosciami

    def accessory_decoder_information_request(self):
        cmd = "fffe42 address 80 + N XOR"   #ustalic
        self.send_data(cmd)

    def accessory_decoder_operation_request(self):
        cmd = "fffe52 address 80 + DBBD XOR"   #ustalic
        self.send_data(cmd)

    def locomotive_information_requests(self, address):
        cmd = "fffee300000" + address + XOR     #ustalic XOR
        self.send_data(cmd)

    def function_status_request(self, number):
        cmd = "fffee307000" + number + XOR     #ustalic XOR
        self.send_data(cmd)

    def locomotive_speed_and_direction_operations(self, address):
        cmd = "fffee410000" + address + RV + XOR     #ustalic RV, XOR
        self.send_data(cmd)

    def function_operation_instructions(self, address):
        cmd = "fffee420000" + address + group + XOR    #ustalic XOR
        self.send_data(cmd)

    def set_function_state(self, address):
        cmd = "fffee424000" + address + group + XOR    #ustalic XOR
        self.send_data(cmd)

    def establish_double_header(self, address1, address2):
        cmd = "fffee543000" + address1 + "000" + address2 + XOR    #ustalic XOR
        self.send_data(cmd)

    def dissolve_double_header(self, address):
        cmd = "fffee543000" + address + "0000" + XOR    #ustalic XOR
        self.send_data(cmd)

    def operations_mode_programming_byte_mode_write_request(self, address):
        cmd = "fffee630000" + address + "ec + c" + cv +d + XOR   #ustalic XOR
        self.send_data(cmd)

    def operations_mode_programming_bit_mode_write_request(self, address):
        cmd = "fffee630000" + address + "e8 + cc" + cv +value/bit + XOR   #ustalic XOR
        self.send_data(cmd)

    def add_a_locomotive_to_a_multi_unit_request(self, address, R):
        cmd = "fffee44" + R + "000" + address + MTR + XOR   #ustalic XOR, MTR=1-99
        self.send_data(cmd)                                 #R=0 jesli kierunek sie zgadza, R=1 jesli jest przeciwny

    def remove_a_locomotive_from_a_multi_unit_request(self, address):
        cmd = "fffee442000" + address + MTR + XOR
        self.send_data(cmd)

    def address_inquiry_member_of_a_multi_unit_request(self, address, R):
        cmd = "fffee401 + R" + MTR+ "000" + address + XOR
        self.send_data(cmd)

    def address_inquiry_multi_unit_request(self, R):
        cmd = "fffee203 + R" + MTR + XOR
        self.send_data(cmd)

    def address_inquiry_locomotive_at_command_station_stack_request(self, address, R):
        cmd = "fffee305 + R" + "000" + address + XOR
        self.send_data(cmd)

    def delete_locomotive_from_command_station_stack_request(self, address):
        cmd = "fffee344000" + address + XOR
        self.send_data(cmd)

if __name__ == '__main__':
    kom = TrainCommunicator()
    kom.connect('192.168.0.200', 5550)
    kom.mushroom_stop()