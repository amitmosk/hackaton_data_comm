import socket
import sys,select
from colors import bcolors

RESERVED_PORTS = 120
TEAM_NAME = "green apes\n"
UDP_IP = "127.0.0.1"
UDP_PORT = 13117

def check_offer_message(msg):
    # divide message
    magic = msg[0:4]
    msg_type = msg[4]
    host_port = msg[5:7]

    if (msg_type != 2):
        print(f"{bcolors.RED}Illegal message type")
        return -1
    if (magic != b"\xab\xcd\xdc\xba"):
        print(f"{bcolors.RED}Illegal message magic number")
        return -1
    ans = int.from_bytes(host_port, "big")
    if ans > RESERVED_PORTS:
        return ans
    else:
        print(f"{bcolors.RED}Illegal host port")
        return -1

class Client:
    def __init__(self):
        self.TCP_socket = None
        self.start_client()

    def start_client(self):
        server_ip, server_port, failed = self.state_1()
        if failed:
            return
        print(f"{bcolors.OKBLUE}Received offer from " + server_ip + ", attempting to connect...")
        failed = self.state_2(server_ip, server_port)
        if failed:
            return
        self.state_3()
        try:
            # closing TCP socket
            self.TCP_socket.close()
            print(f"{bcolors.RED}Server disconnected, listening for offer requests...")
        except Exception as e:
            print(f"{bcolors.RED}Failed closing TCP socket")
            print(e)

    def state_1(self):
        # -- CREATE UDP SOCKET
        print(f"{bcolors.OKBLUE}Client started, listening for offer requests...{bcolors.RED}")
        try:
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            UDP_socket.bind((UDP_IP, UDP_PORT))
            offer_message, addr = UDP_socket.recvfrom(1024)
            server_port = check_offer_message(offer_message)
            server_ip = addr[0]
            UDP_socket.close()
            if server_port == -1:
                print(f"{bcolors.RED}Broken message from server")
                return server_ip, server_port, True
            else:
                return server_ip, server_port, False
        except Exception as err:
            print(f"{bcolors.RED}UDP socket creation & get broadcast message failed with error %s" % (err))
            UDP_socket.close()
            return None, None, True

    def state_2(self, server_ip, server_port):
        try:
            # create TCP socket
            TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect TCP server socket
            TCP_socket.connect((server_ip, server_port))
            self.TCP_socket = TCP_socket
            return False
        except Exception as err:
            print(f"{bcolors.RED}TCP socket creation & connect to the server failed with error %s" % (err))
            TCP_socket.close()
            return True

    def state_3(self):
        try:
            # send team name to the server
            self.TCP_socket.send(TEAM_NAME.encode())
        except Exception as e:
            print(f"{bcolors.RED}Failed sending team name message")
            print(e)
            return
        try:
            # get & print the question
            print(self.TCP_socket.recv(1024).decode())
            # getting answer from user
            our_answer = input(f"{bcolors.PINK}Enter your answer:")
        except Exception as e:
            print(f"{bcolors.RED}Failed getting the question message")
            print(e)
            return
        try:
            # send our answer to the server
            self.TCP_socket.send(our_answer.encode())
        except Exception as e:
            print(f"{bcolors.RED}Failed sending the answer message")
            print(e)
            return
        try:
            # get the summary from server
            print(f"{bcolors.OKGREEN}--------------")
            print(self.TCP_socket.recv(1024).decode())
        except Exception as e:
            print(f"{bcolors.RED}Failed getting the summary message")
            print(e)
            return
