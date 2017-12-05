import socket
import threading
from client import Client
from server import Server
from coordinator import Coordinator
import time
import json
import util

GENERATOR = 850814731652311369604857817867299164248640829807806264080080192664697908283
MODULO = 78259045243861432232475255071584746141480579030179831349765025070491917900839

def main():

    coordinator = Coordinator(GENERATOR, MODULO, "127.0.0.1", 5003)
    thread1 = threading.Thread(target=coordinator.listenAndCoordinate)
    thread1.daemon = True
    thread1.start()

    while True:
        try:
        	command = input("> ")
        except KeyboardInterrupt:
        	print("quitting")
        	quit()

        args = command.split()

        if args[0] == "next_round":
            print("Here")
            coordinator.startNextRound()


if __name__ == "__main__":
    main()
