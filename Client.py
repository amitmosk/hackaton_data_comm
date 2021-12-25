# An example script to connect to Google using socket
# programming in Python
import socket  # for socket
import sys
from colors import bcolors


class Client:
    def __init__(self):
        self.team_name = "green apes\n"
        self.RESERVED_PORTS = 120
        self.start_client()

    def start_client(self):
        ## ------------------ STATE 1 -------------------------------------------------------
        print(f"{bcolors.OKBLUE}Client started, listening for offer requests...{bcolors.RED}")
        try:
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as err:
            print(f"{bcolors.RED}socket creation failed with error %s" % (err))
            self.start_client()
            return

        UDP_IP = "555.555.55.5555"
        UDP_PORT = 13117
        # UDP_socket.bind()
        # receive broadcast via UDP
        try:
            offer_message, server_ip = UDP_socket.recvfrom(1024)
            server_port = self.check_offer_message(offer_message)
            if server_port == -1:
                UDP_socket.close()
                self.start_client()
                return
        except Exception as err:
            UDP_socket.close()
            print(err)
            print(f"{bcolors.RED}cant receive from UDP connection")
            self.start_client()
            return

        print(f"{bcolors.OKBLUE}Received offer from " + server_ip + ", attempting to connect...")
        ## ------------------ STATE 2 -------------------------------------------------------
        # create TCP socket
        try:
            TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            print(f"{bcolors.RED}socket creation failed with error %s" % (err))
            UDP_socket.close()
            self.start_client()
            return

        # connect TCP server socket
        try:
            TCP_socket.connect((server_ip, server_port))
        except socket.error as e:
            print(e)
            UDP_socket.close()
            TCP_socket.close()
            print(f"{bcolors.RED}cant connect to server")
            self.start_client()
            return

        ## ------------------ STATE 3 -------------------------------------------------------

        # closing UDP connection
        UDP_socket.close()
        # send team name to the server
        send_name_flag = False
        while not send_name_flag:
            try:
                TCP_socket.send(self.team_name.encode())
                send_name_flag = True
            except socket.error as e:
                print(e)
                print(f"{bcolors.RED}didnt send team name message, try again..")

        # get & print the question
        get_question_flag = False
        while not get_question_flag:
            try:
                print(TCP_socket.recv(1024).decode())
                get_question_flag = True
                our_answer = input(f"{bcolors.PINK}Enter your answer:")
            except Exception as e:
                print(e)
                print(f"{bcolors.RED}didnt got the question message, try again..")

        # send our answer to server
        send_answer_flag = False
        while not send_answer_flag:
            try:
                TCP_socket.send(our_answer.encode())
                send_answer_flag = True
            except Exception as e:
                print(e)
                print(f"{bcolors.RED}didnt send the answer message, try again..")

        # get the summary
        get_summary_flag = False
        while not get_summary_flag:
            try:
                print(f"{bcolors.OKGREEN}--------------")
                print(TCP_socket.recv(1024).decode())
                get_summary_flag = True
            except Exception as e:
                print(e)
                print(f"{bcolors.RED}didnt got the summary message, try again..")

        TCP_socket.close()


    def check_offer_message(self, msg):
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
        if ans > self.RESERVED_PORTS:
            return ans
        else:
            print(f"{bcolors.RED}Illegal host port")
            return -1