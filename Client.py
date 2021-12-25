# An example script to connect to Google using socket
# programming in Python
import socket  # for socket
import sys

try:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # AF_INET - the address-family ipv4
    # SOCK_STREAM - connection-oriented TCP protocol
    print("Socket successfully created")
except socket.error as err:
    print("socket creation failed with error %s" % (err))
port = 80
try:
    host_ip = socket.gethostbyname('www.google.com')
except socket.gaierror:
    # this means could not resolve the host
    print("there was an error resolving the host")
    sys.exit()

# connecting to the server
s.connect((host_ip, port))

print("the socket has successfully connected to google")

print(s.recv(1024).decode())
# close the connection
s.close()

while True:
    team_name = "green apes\n"
    ## ------------------ STATE 1 -------------------------------------------------------
    print("Client started, listening for offer requests...")
    try:
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    UDP_IP = "555.555.55.5555"
    UDP_PORT = 13117
    # receive broadcast via UDP
    offer_message, addr = UDP_socket.recvfrom(1024)
    host_ip = offer_message[555555]
    server_port = offer_message[555]
    print("Received offer from " + addr + ", attempting to connect...")
    ## ------------------ STATE 2 -------------------------------------------------------
    try:
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    TCP_socket.connect((host_ip, port))
    ## ------------------ STATE 3 -------------------------------------------------------
    UDP_socket.close()
    TCP_socket.send(team_name.encode())
    # get & print the question
    print(TCP_socket.recv(1024).decode())
    our_answer = input("Enter your answer:")
    TCP_socket.send(our_answer.encode())
    # get the summary
    print(TCP_socket.recv(1024).decode())
    TCP_socket.close()
