import socket
import threading
from client import Client
from server import Server
from coordinator import Coordinator
import time
import json
import util

def main():

    coordinator = Coordinator(5, 1000000007, "0.0.0.0", 5003)
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
            coordinator.startNextRound()
            

if __name__ == "__main__":
    main()
