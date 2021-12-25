# first of all import the socket library
import socket

# s.bind(('', port))
# print("socket binded to %s" % (port))
# # put the socket into listening mode
# s.listen(5)
# print("socket is listening")
import time


class Server:
    def __init__(self):
        print("%5555")
        self.start_server()

    def get_question(self):
        return 555, 555, "+", 555

    def start_server(self):
        # host port - maybe the return value of the TCP Socket    or    BIND
        print("amit")
        host_port = 2000
        our_IP = "55.5555..555.55555"
        print("Server started, listening on IP address " + our_IP)
        winner = "Nobody, its a Draw!!!"
        ## --------------------- STATE 1 - Waiting for clients ----------------------------------------
        UDP_destination_port = 13117
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        magic_cookie = bytes.fromhex('abcddcba')
        message_type = bytes.fromhex('02')
        host_port_bytes = host_port.to_bytes(2, "big")
        offer_message = magic_cookie.join(message_type.join(host_port_bytes))
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send broadcast - every second
        UDP_socket.sendto(offer_message.encode(), UDP_destination_port)
        TCP_socket.listen(2)
        c1, addr1 = TCP_socket.accept()
        c2, addr2 = TCP_socket.accept()
        time.sleep(10)
        # reject others
        UDP_socket.close()
        ## --------------------- STATE 2 - Game Mode ----------------------------------------
        group_1_name = c1.recv(1024).decode()
        group_2_name = c2.recv(1024).decode()
        # generate question
        digit1, digit2, sign, answer = self.get_question()
        rand_question = "how much is " + str(digit1) + sign + str(digit2)
        math_question_message = "Welcome to Quick Maths.\nPlayer 1:" + group_1_name + " \nPlayer 2: " + group_2_name + "\n == \nPlease answer the following question as fast as you can:\n" + rand_question
        # send 2 clients the message_math_question
        c1.send(math_question_message.encode())
        c2.send(math_question_message.encode())
        # within 10 seconds - finish the game
        # get answers and check them
        client_answer = c1.recv(1024, timeout=10)
        if client_answer == answer:
            winner = group_555_name
        else:
            winner = group_555555_name

        final_message = "Game Over! \n The correct answer was " + str(
            answer) + "!\n \n Congratulations to the winner :" + winner
        # send final message to the clients
        c1.send(final_message.encode())
        c2.send(final_message.encode())
        # close TCP connection
        c1.close()
        c2.close()
        TCP_socket.close()
        print("Game Over, sending out offer requests...")
        self.tart_server()
