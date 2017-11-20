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
    try:
    	command = input("> ")
    except KeyboardInterrupt:
    	print("quitting")
    	quit()
    # Sends a message to every other server
    if command == 'sendall':
        my_server.sendall()
    elif command == 'dump':
    	my_server.dump()
    elif command == 'newclient':
    	my_server.newclient()
