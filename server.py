import socket
import threading
import random
import util
from client import Client
from ledger import Ledger

#We hardcode all the available ports to make things easy
ALL_PORTS = [5000, 5001, 5002]
COORDINATOR_PORT = 5003

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
        self.MY_CLIENTS = {}
        self.newclient()

        ### MESSAGE CREATION ###
        # Everyone has their own log of messages, every time we get a message append to log
        self.MY_MESSAGES = {}

        ### LEDGER CREATION ###
        ### we can have the ledgers be in just the clients or just the servers or both
        self.MY_LEDGER = Ledger()

    def listen(self):
        while True:
            data, addr = self.receivesocket.recvfrom(1024) # buffer size is 1024 bytes
            data = util.deserialize(data).decode()
            if data['msg_type'] == 'SHUFFLE_START':
                client_ids = data['client_id']
                public_keys = data['public_key']
            elif data['msg_type'] == 


    # Send a message to every port which is not yourself
    def sendall(self, data):
        for port in ALL_PORTS:
            if port != self.MY_PORT:
                util.sendDict(data, self.MY_IP, port, self.sendsocket)

    def sendtocoordinator(self, data):
        util.sendDict(data, self.MY_IP, COORDINATOR_PORT, self.sendsocket)

    def postmessage(self, client_id, reputation, message):
        if client_id not in self.MY_CLIENTS:
            print("Unknown client")
            return
        # self.MY_MESSAGES[client_id] = message

        # signing??? should be implemented in client.py to use and sign
        # signed = self.MY_CLIENTS[client_id].generate_signed_messages(message)
        # print(signed)

        # Calculate amount of reputation 
        if len(self.MY_CLIENTS[client_id].wallets) < reputation:
            print("Not enough reputation points")
            return

        wallet_signatures = []
        for i in range(reputation):
            wallet_signatures.append(self.MY_CLIENTS[client_id].wallets[i]['PublicKey'])

        new_message = {
            'msg_type': message,
            'signatures': wallet_signatures,    
        }
        # Post to coordinator
        self.sendtocoordinator(new_message)

    def dumpmessages(self):
        # is this supposed to dump messages on the current server or after aggregation?
        print("not implemented")

    def broadcastmessages(self):
        for client_id, message in self.MY_MESSAGES:
            print("%s: %s", client_id, message)

    def newclient(self):
        #TODO, decide on a naming scheme for client
        new_client = Client(str(self.MY_PORT) + str(random.randint(1, 100)))
        print("Server: Client {} created".format(new_client.client_id))
        data = dict()
        data['type'] = 'new_client'
        data['client_id'] = new_client.client_id
        data['public_key'] = new_client.public_key
        self.sendtocoordinator(data)

    def upvote(self, client_id, message_id):
        # TODO: Linkable ring signature + upvote
        print("nope")
    def downvote(self, client_id, message_id):
        # TODO: Linkable ring signature + downvote
        print("nope")

    # We probably need to classify all the messages that we'll be receiving

    def received_posted_message(self, message):
        print("not yet implemented")
    def received_voting_message(self, message):
        print("not yet implemented")
    def received_ledger_update(self, message):
        print("not yet implemented")
        # there will be different reasons for the ledger being updated:
        # - received a broadcast to update the ledger
        # - received a broadcast to propose a change to the ledger
        # -----> would then need to try to get a signature for the proposed block
