import socket
import threading
from server import Server
from client import Client

UDP_IP = 5000

my_server = Server()

threading1 = threading.Thread(target=my_server.listen)
threading1.daemon = True
threading1.start()

# User input
while True:
    command = input("> ")
    # Sends a message to every other server
    if command == 'sendall':
        my_server.sendall()
