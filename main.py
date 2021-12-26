# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from Client import Client
from Server import Server
from colors import bcolors

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        print(f"{bcolors.PINK}Welcome To Green Apes Jungle! please choose an option")
        print(f"{bcolors.YELLOW}1) Server")
        print(f"{bcolors.YELLOW}2) Client")
        good_choise = False
        while not good_choise:
            user_choise = input()
            if user_choise == "1":
                server = Server()
                good_choise = True
            if user_choise == "2":
                client = Client()
                good_choise = True
            else:
                print(f"{bcolors.RED}Please Try Again..")

