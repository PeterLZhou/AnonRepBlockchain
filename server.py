import socket
import threading
from client import Client

#We hardcode all the available ports to make things easy
ALL_PORTS = [5000, 5001, 5002]

class Server():
    def __init__(self):
        # Used for the server to send outbound messages
        self.sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Used for the server to receive inbound messages
        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        ### SOCKET CREATION ###
        # Creates a socket at localhost and next available 5000 client
        self.MY_IP = "0.0.0.0"
        self.MY_PORT = 5000
        connected = False
        while not connected:
            try:
                self.receivesocket.bind((self.MY_IP, self.MY_PORT))
                print("Connected to port ", self.MY_PORT)
                connected = True
            except:
                print("Port {} is probably in use".format(self.MY_PORT))
                self.MY_PORT += 1

        ### CLIENT CREATION ###
        # Everyone creates one client on startup
        self.MY_CLIENTS = {}
        new_client = Client(self.MY_PORT)
        self.MY_CLIENTS[new_client.client_id] = new_client
        print("Client {} added".format(new_client.client_id))
        print("Client private key: ", new_client.private_key)
        ### MESSAGE CREATION ###
        # Everyone has their own log of messages, every time we get a message append to log
        self.MY_MESSAGES = {}


    def listen(self):
        while True:
            data, addr = self.receivesocket.recvfrom(1024) # buffer size is 1024 bytes
            data = data.decode()
            self.MY_MESSAGES.append(data)
            print("I got it: ", data)

    # Send a message to every port which is not yourself
    def sendall(self):
        client_id = "None"
        message = "TEST MESSAGE"
        self.MY_MESSAGES[client_id] = message
        for port in ALL_PORTS:
            if port != self.MY_PORT:
                self.sendsocket.sendto(message.encode(), (self.MY_IP, port))

    def postmessage(self, client_id, message):
        self.MY_MESSAGES[client_id] = message
        # TODO: Broadcast stuff

    def broadcastmessages(self):
        for client_id, message in self.MY_MESSAGES:
            print("%s: %s", client_id, message)

    def newclient(self):
        #TODO, decide on a naming scheme for client
        new_client = Client(self.MY_PORT + str(rand(100)))
        self.MY_CLIENTS[new_client.client_id] = new_client
        print("Client {} added".format(new_client.client_id))

    def upvote(self, client_id, message_id):
        # TODO: Linkable ring signature + upvote
        print("nope")
    def downvote(self, client_id, message_id):
        # TODO: Linkable ring signature + downvote
        print("nope")
