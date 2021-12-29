# first of all import the socket library
import random
import socket
from socket import *
import threading
from threading import Timer
import time

# s.bind(('', port))
# print("socket binded to %s" % (port))
# # put the socket into listening mode
# s.listen(5)
# print("socket is listening")
from colors import bcolors

finish_broadcast_flag = False
finish_game_flag = False
winner = ["Nobody, its a Draw!!!"]
UDP_destination_port = 13117
timeout = 10
magic_cookie_str = 'abcddcba'
message_type_str = '02'
stat_table = {}

def build_msg(host_port):
    # build the message according the format
    magic_cookie = bytes.fromhex(magic_cookie_str)
    message_type = bytes.fromhex(message_type_str)
    host_port_bytes = host_port.to_bytes(2, "big")
    offer_message = b''.join([magic_cookie, message_type, host_port_bytes])
    return offer_message
def get_question():
    is_bad_answer = True
    while is_bad_answer:
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
            rand_question = "how much is " + str(param1) + sign + str(param2)
            is_bad_answer = False
    return rand_question, answer


def add_to_stat(group_1_name, group_2_name):
        global stat_table
        if group_1_name not in stat_table.keys:
            stat_table[group_1_name] = 0
        if group_2_name not in stat_table.keys:
            stat_table[group_2_name] = 0

def update_points(winner, looser, tie):
    if tie:
        stat_table[winner] +=1
        stat_table[looser] +=1 
    else:
        stat_table[winner] +=3
        stat_table[looser] -=1    


class Server:

    def __init__(self):
    
        self.our_IP = "127.0.0.1"
        while True:
            self.start_server()
            self.reset_values()

    def start_server(self):
        # host port
        UDP_addr = (self.our_IP, UDP_destination_port)
        print(f"{bcolors.OKBLUE}Server started, listening on IP address " + self.our_IP)
        # --------------------------------------------------------------- STATE 1 - Waiting for clients ------------------------------------------------------------

        # -- Create TCP socket
        TCP_socket, host_port, failed = self.create_bind_TCP_socket()
        if failed:
            return

        # Build offer for clients
        offer_message = build_msg(host_port)
        # -- Create UDP socket
        UDP_socket, failed = self.create_UDP_socket()
        if failed:
            return
        # -- Set TCP socket to listen to maximum 2 clients
        try:
            TCP_socket.listen(2)
        except Exception as e:
            print(f"{bcolors.RED}Error in TCP socket")
            print(e)
            TCP_socket.close()
            return

        # -- Create thread to manage broadcast sends
        send_broadcast = Send_UDP_thread(offer_message, UDP_socket, UDP_addr)
        send_broadcast.start()
        # -- Establish connection with client
        try:
            c1, addr1 = TCP_socket.accept()
            c2, addr2 = TCP_socket.accept()

            # -- Set flag to kill sending thread
            global finish_broadcast_flag
            finish_broadcast_flag = True
        except Exception as e:
            print(f"{bcolors.RED}Error in TCP socket")
            print(e)

        send_broadcast.join()
        # --------------------------------------------------------------- STATE 2 - Game Mode ------------------------------------------------------------
        # receive group names from the clients
        c1.settimeout(timeout)
        c2.settimeout(timeout)

        # -- Wait 10 second before starting the game
        time.sleep(timeout)
        
        group_1_name, group_2_name = self.receive_group_names(c1, c2)

        if group_1_name is None or group_2_name is None:
            TCP_socket.close()
            c1.close()
            c2.close()
            return
        
        group_1_name = "a"
        group_2_name = "b"
        #adding the groups to the statistics table
        add_to_stat(group_1_name, group_2_name)
        
        # generate question
        rand_question, answer = get_question()
        math_question_message = "Welcome to Quick Maths.\nPlayer 1:" + group_1_name + " \nPlayer 2: " + group_2_name + \
                                "\n == \nPlease answer the following question as fast as you can:\n" + rand_question
        # set flag to stop the game
        t1 = Client_thread(c1, math_question_message, answer, group_1_name, group_2_name)
        t2 = Client_thread(c2, math_question_message, answer, group_2_name, group_1_name)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        final_message = "Game Over! \nThe correct answer was " + str(answer) + "!\n \nCongratulations to the winner : " + winner[0] + '\n'
        group_1_name+" points: "+ str(stat_table[group_1_name]) + "\n" + group_2_name + " points: " + str(stat_table[group_2_name])
        
        #if tie
        if winner[0] == "Nobody, its a Draw!!!": 
            update_points(group_1_name,group_2_name, True)
        # send final message to the clients
        try:
            c1.send(final_message.encode())
            c2.send(final_message.encode())
        except Exception as e:
            print(f"{bcolors.RED}Failed sending final message")
            print(e)

        # close TCP connection
        try:
            c1.close()
            c2.close()
            TCP_socket.close()
        except Exception as e:
            print(f"{bcolors.RED}Failed closing sockets")
            print(e)
        # print game summary
        print(f"{bcolors.OKBLUE} summary:" + final_message)
        print(f"{bcolors.OKBLUE}Game Over, sending out offer requests...")

    
    def reset_values(self):
        global finish_broadcast_flag
        finish_broadcast_flag = False
        global finish_game_flag
        finish_game_flag = False
        global winner
        winner = ["Nobody, its a Draw!!!"]

    def create_UDP_socket(self):
        try:
            UDP_socket = socket(AF_INET, SOCK_DGRAM)
            # -- Set UDP socket flags to support multiple clients
            UDP_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            UDP_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            return UDP_socket, False
        except Exception as e:
            print(f"{bcolors.RED}Failed in open an UDP socket")
            print(e)
            UDP_socket.close()
            return None, True

    def create_bind_TCP_socket(self):
        try:
            # create TCP socket
            TCP_socket = socket(AF_INET, SOCK_STREAM)
            TCP_socket.bind(('', 0))
            #host_port = TCP_socket.gethostbyname(socket.gethostname())
            host_port = TCP_socket.getsockname()[1]
            return TCP_socket, host_port, False
        except Exception as e:
            print(f"{bcolors.RED}Failed in open a TCP socket")
            print(e)
            TCP_socket.close()
            return None, None, True

    def receive_group_names(self, c1, c2):
        #receive_flag = False

        try:
            # receive group names from the clients
            group_1_name = c1.recv(1024).decode()
            group_2_name = c2.recv(1024).decode()
            #receive_flag = True
            return group_1_name, group_2_name
        except socket.error as e:
            print(f"{bcolors.RED}didnt receive team name message, try again..")
            print(e)
            return None, None
    



class Client_thread(threading.Thread):
    def __init__(self, connection, question, answer, myName, opponnetName):
        threading.Thread.__init__(self)
        self.connection = connection
        self.question = question
        self.answer = answer
        self.myName = myName
        print(myName)
        self.opponnetName = opponnetName

    def run(self):
        try:
            # send meesage
            self.connection.send(self.question.encode())
            # get answer and check
            client_answer = self.connection.recv(1024).decode()
            self.finish_game(client_answer)
        except Exception as e:
            # draw
            pass

    def finish_game(self, client_answer):
        global finish_game_flag
        #finish_game_flag = False
        global winner
        if finish_game_flag is False:
            if int(client_answer) == self.answer:
                winner[0] = self.myName
                update_points(self.myName, self.opponnetName, False)
            else:
                winner[0] = self.opponnetName
                update_points(self.opponnetName, self.myName, False)
                
            finish_game_flag = True


class Send_UDP_thread(threading.Thread):
    def __init__(self, offer_message, UDP_socket, UDP_addr):
        threading.Thread.__init__(self)
        self.offer_message = offer_message
        self.UDP_socket = UDP_socket
        self.UDP_addr = UDP_addr

    def run(self):
        global finish_broadcast_flag
        finish_broadcast_flag = False
        # send broadcast - every second
        while finish_broadcast_flag is False:
            time.sleep(1)
            try:
                self.UDP_socket.sendto(self.offer_message, self.UDP_addr)
                print("send broadcast")
            except Exception as e:
                pass
        # closing UDP socket
        try:
            self.UDP_socket.close()
            print("closing UDP socket")
        except Exception as e:
            pass
