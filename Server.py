# first of all import the socket library
import random
import socket
from socket import *
import threading
import time


# s.bind(('', port))
# print("socket binded to %s" % (port))
# # put the socket into listening mode
# s.listen(5)
# print("socket is listening")
from colors import bcolors


class Server:
    def __init__(self):
        self.start_server()

    def get_question(self):
        param1 = random.randint(1, 10)
        param2 = random.randint(1, 10)
        sign_rand = random.randint(0, 3)
        answer = -1
        sign = ""
        if sign_rand == 0:
            answer = param1 + param2
            sign = "+"
        if sign_rand == 1:
            if param1 < param2:
                temp = param2
                param2 = param1
                param1 = temp
            answer = param1 - param2
            sign = "-"
        if sign_rand == 2:
            answer = param1 * param2
            sign = "*"
        if sign_rand == 3:
            if param1 % param2 == 0:
                answer = int(param1 / param2)
                sign = "/"
        if -1 < answer < 10:
            return param1, param2, sign, answer
        else:
            return self.get_question()

    def start_server(self):
        # host port - maybe the return value of the TCP Socket    or    BIND
        our_IP = "55.5555..555.55555"
        print(f"{bcolors.OKBLUE}Server started, listening on IP address " + our_IP)
        ## --------------------- STATE 1 - Waiting for clients ----------------------------------------
        UDP_destination_port = 13117
        UDP_addr = ("127.0.0.1", UDP_destination_port)
        # TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket = socket(AF_INET, SOCK_STREAM)
        TCP_socket.bind(('', 0))
        host_port = TCP_socket.getsockname()[1]
        # TCP_socket.bind((our_IP, host_port))
        # build the message according the format
        magic_cookie = bytes.fromhex('abcddcba')
        message_type = bytes.fromhex('02')
        host_port_bytes = host_port.to_bytes(2, "big")
        offer_message = b''.join([magic_cookie, message_type, host_port_bytes])
        # UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket = socket(AF_INET, SOCK_DGRAM)
        # send broadcast - every second
        UDP_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        UDP_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # UDP_socket.bind(('', UDP_destination_port))
        # UDP_socket.sendto(offer_message, ("", UDP_destination_port))
        TCP_socket.listen(2)
        send_thread_flag = ["amit"]
        send_brodcast = Send_UDP_thread(offer_message, UDP_socket, UDP_addr, send_thread_flag)
        send_brodcast.start()
        c1, addr1 = TCP_socket.accept()
        # c2, addr2 = TCP_socket.accept()
        send_thread_flag[0] = "True"
        print("its changed")
        send_brodcast.join()
        time.sleep(10)
        UDP_socket.close()
        ## --------------------- STATE 2 - Game Mode ----------------------------------------
        group_1_name = c1.recv(1024).decode()
        # group_2_name = c2.recv(1024).decode()
        # generate question
        digit1, digit2, sign, answer = self.get_question()
        rand_question = "how much is " + str(digit1) + sign + str(digit2)
        math_question_message = "Welcome to Quick Maths.\nPlayer 1:" + group_1_name + " \nPlayer 2: " + "group_2_name" + "\n == \nPlease answer the following question as fast as you can:\n" + rand_question
        # within 10 seconds - finish the game
        flag = [False]
        winner = ["Nobody, its a Draw!!!"]
        t1 = Client_thread(c1, math_question_message, answer, group_1_name, "group_2_name", flag, winner)
        # t2 = Client_thread(c2, math_question_message, answer, group_2_name, group_1_name, flag, winner)
        t1.start()
        # t2.start()
        t1.join()
        # t2.join()
        final_message = "Game Over! \nThe correct answer was " + str(answer) + "!\n \nCongratulations to the winner : " + winner[0]
        # send final message to the clients
        c1.send(final_message.encode())
        # c2.send(final_message.encode())
        # close TCP connection
        c1.close()
        # c2.close()
        TCP_socket.close()
        print(f"{bcolors.OKBLUE} summary:" + final_message)
        print(f"{bcolors.OKBLUE}Game Over, sending out offer requests...")
        self.start_server()

class Client_thread(threading.Thread):
    def __init__(self, connection, question, answer, myName, opponnetName, flag, winner):
        threading.Thread.__init__(self)
        self.connection = connection
        self.question = question
        self.answer = answer
        self.myName = myName
        print(myName)
        self.opponnetName = opponnetName
        self.flag = flag
        self.winner = winner

    def run(self):
        self.connection.send(self.question.encode())
        try:
            # send client the message_math_question
            self.connection.settimeout(10)
            # get answer and check
            client_answer = self.connection.recv(1024).decode()
            self.finish_game(client_answer)
        except Exception as e:
            # draw
            print(f"{bcolors.YELLOW}PASS")
            pass

    def finish_game(self, client_answer):
        if self.flag == [False]:
            if int(client_answer) == self.answer:
                self.winner[0]= self.myName
                print(f"{bcolors.YELLOW}1111")
            else:
                self.winner[0] = self.opponnetName
                print(f"{bcolors.YELLOW}222222222")

            self.flag = [True]




class Send_UDP_thread(threading.Thread):
    def __init__(self, offer_message, UDP_socket, UDP_addr, flag):
        threading.Thread.__init__(self)
        self.offer_message = offer_message
        self.UDP_socket = UDP_socket
        self.UDP_addr = UDP_addr
        self.flag = flag


    def run(self):
        while self.flag[0] == "amit":
            time.sleep(1)
            self.UDP_socket.sendto(self.offer_message,  self.UDP_addr)