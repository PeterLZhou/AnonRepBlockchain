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
        #Used for the shuffle protocol
        self.randomnumber = (int) (random.random() * 1000)

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

        ### LEDGER CREATION ###
        ### we can have the ledgers be in just the clients or just the servers or both
        self.MY_LEDGER = Ledger()

    def listen(self):
        while True:
            data, addr = self.receivesocket.recvfrom(100000) # buffer size is 1024 bytes
            data = util.readDict(data)
            if data['msg_type'] == 'SHUFFLE':
                wallet_list = data['wallet_list']
                g = data['g']
                p = data['p']
                server_list = data['server_list']
                self.shuffle(wallet_list, g, p, server_list)
            elif data['msg_type'] == 'TEST':
                print(data['message'])
            elif data['msg_type'] == 'NYM_ANNOUNCE':
                nym_map = data['nym_map']
                gen_powered = data['gen_powered']
                self.shownyms(nym_map)

    def send(self, data, ip_addr, port):
        util.sendDict(data, ip_addr, port, self.sendsocket)

    # Send a message to every port which is not yourself
    def sendall(self, data):
        for port in ALL_PORTS:
            if port != self.MY_PORT:
                util.sendDict(data, self.MY_IP, port, self.sendsocket)

    def sendtocoordinator(self, data):
        util.sendDict(data, self.MY_IP, COORDINATOR_PORT, self.sendsocket)

    def postmessage(self, client_id, message):
        if client_id not in self.MY_CLIENTS:
            print("Unknown client")
            return
        self.MY_MESSAGES[client_id] = message
        # Calculate amount of reputation to use and sign
        signed = self.MY_CLIENTS[client_id].generate_signed_messages(message)
        print(signed)
        # TODO: Post to single server or broadcast to all?

    def broadcastmessages(self):
        for client_id, message in self.MY_MESSAGES:
            print("%s: %s", client_id, message)

    def newclient(self):
        #TODO, decide on a naming scheme for client
        new_client = Client(str(self.MY_PORT) + str(random.randint(1, 100)))
        self.MY_CLIENTS[new_client.client_id] = new_client
        print("Server: Client {} created".format(new_client.client_id))
        data = dict()
        data['msg_type'] = 'NEW_WALLET'
        data['public_key'] = new_client.wallets[0]['public_key']
        self.sendtocoordinator(data)

    def shuffle(wallet_list, g, p, server_list):
        server_idx = server_list.index((self.MY_IP, self.MY_PORT))
        new_wallet_list = [(wallet ** self.randomnumber) % p for wallet in wallet_list]
        new_g = (g ** self.randomnumber) % p
        new_dict = dict()
        if server_idx == len(server_list) - 1:
            receiver = (self.MY_IP, COORDINATOR_PORT)
            new_dict['msg_type'] = 'SHUFFLE_END'
        else:
            receiver = (self.MY_IP, server_list[server_idx + 1][1])
            new_dict['msg_type'] = 'SHUFFLE'
        new_dict['wallet_list'] = new_wallet_list
        new_dict['g'] = new_g
        new_dict['p'] = p
        new_dict['server_list'] = server_list
        self.send(new_dict, receiver[0], receiver[1])

    def shownyms(self, nym_map):
        for nym in nym_map:
            print(nym)
            print("Reputation: 1")

    def upvote(self, client_id, message_id):
        # TODO: Linkable ring signature + upvote
        print("nope")
    def downvote(self, client_id, message_id):
        # TODO: Linkable ring signature + downvote
        print("nope")
