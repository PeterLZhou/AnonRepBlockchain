import socket
import threading
import random
import util
from client import Client
from ledger import Ledger

#We hardcode all the available ports to make things easy
ALL_PORTS = [5000, 5001, 5002]
COORDINATOR_PORT = 5003
MODULO = 78259045243861432232475255071584746141480579030179831349765025070491917900839
P = 78259045243861432232475255071584746141480579030179831349765025070491917900839
G = 850814731652311369604857817867299164248640829807806264080080192664697908283

class Server():
    def __init__(self):
        # Used for the server to send outbound messages
        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Used for the server to receive inbound messages
        # self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        #Used for the shuffle protocol
        self.randomnumber = (int) (random.random() * 1000)

        ### SOCKET CREATION ###
        # Creates a socket at localhost and next available 5000 client
        self.MY_IP = "127.0.0.1"
        self.MY_PORT = 5000
        self.CURRENT_GEN_POWERED = G
        connected = False
        while not connected:
            try:
                self.receivesocket.bind((self.MY_IP, self.MY_PORT))
                print("Connected to port ", self.MY_PORT)
                connected = True
            except:
                print("Port {} is probably in use".format(self.MY_PORT))
                self.MY_PORT += 1

        self.serverjoin()
        ### CLIENT CREATION ###
        self.MY_CLIENTS = {}
        self.newclient()

        self.known_clients = []
        ### LEDGER CREATION ###
        ### we can have the ledgers be in just the clients or just the servers or both
        self.MY_LEDGER = Ledger()

        self.current_round = "NONE"

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
                self.CURRENT_GEN_POWERED = gen_powered
                self.shownyms(nym_map)
                self.current_round = 'POST_MESSAGE'
            elif data['msg_type'] == 'SERVER_JOIN_REPLY':
                print("Server join status: ", data["status"])
            elif data['msg_type'] == 'LEDGER_UPDATE': # a new block has been appended to the blockchain
                self.mergeledger(data)
            elif data['msg_type'] == 'NEW_VOTE': # this server has been selected to be the leader for a new vote
                self.newvoteupdateledger(data)
            elif data['msg_type'] == 'NEW_WALLET': # this server has been selected to be the leader
                self.newwalletupdateledger(data)
            elif data['msg_type'] == 'VOTE_RESULT':
                vote_list = data['wallet_delta'] # a list of objects with structure : {text, id, nyms, votes}
                print(vote_list)
                new_public_keys = self.sendvotestoclients(vote_list)
                for public_key in new_public_keys:
                    newdict = dict()
                    newdict['msg_type'] = 'NEW_WALLET'
                    newdict['public_key'] = public_key
                    self.sendtocoordinator(newdict)
            elif data['msg_type'] == 'GET_VOTE_COUNT':
                self.returnvotecount(data)
            elif data['msg_type'] == 'MESSAGE_BROADCAST':
                text = data['text']
                msg_id = data['id']
                nyms = data['nyms']
                self.showmessage(text, msg_id, nyms)
            elif data['msg_type'] == 'SERVER_JOIN_REPLY':
                print("Server join status: ", data["status"])
            elif data['msg_type'] == 'VOTE_START':
                self.current_round = 'VOTE_START'
                self.MY_LEDGER.ALL_VOTES = {}
                print("Voting round started.")
            elif data['msg_type'] == 'VOTE_END':
                self.current_round = 'SPLIT'
                print("Voting round ended.")
            elif data['msg_type'] == 'CLIENT_ANNOUNCE':
                self.known_clients = data['client_pubkeys']

    def send(self, data, ip_addr, port):
        util.sendDict(data, ip_addr, port, self.receivesocket)

    # Send a message to every port which is not yourself
    def sendall(self, data):
        for port in ALL_PORTS:
            if port != self.MY_PORT:
                util.sendDict(data, self.MY_IP, port, self.receivesocket)

    def sendtocoordinator(self, data):
        util.sendDict(data, self.MY_IP, COORDINATOR_PORT, self.receivesocket)

    def postmessage(self, client_id, reputation, message):
        if client_id not in self.MY_CLIENTS:
            print("Unknown client")
            return
        if self.current_round != "POST_MESSAGE":
            return
        # self.MY_MESSAGES[client_id] = message

        # signing??? should be implemented in client.py to use and sign
        # signed = self.MY_CLIENTS[client_id].generate_signed_messages(message)
        # print(signed)

        # Calculate amount of reputation
        if len(self.MY_CLIENTS[client_id].wallets) < reputation:
            print("Not enough reputation points! Message cannot be posted!")
            return

        wallet_signatures, wallet_pseudonyms = self.MY_CLIENTS[client_id].get_signatures(message, reputation, self.CURRENT_GEN_POWERED)
        for i in range(len(wallet_signatures)):
            print("Verifying message")
            assert(util.elgamalverify(message, wallet_pseudonyms[i], wallet_signatures[i][0], wallet_signatures[i][1], self.CURRENT_GEN_POWERED, P))
            print("Message verified")
        new_message = {
            'msg_type': "MESSAGE",
            'text_msg': message,
            'signatures': wallet_signatures,
            'pseudonyms': wallet_pseudonyms
        }
        # Post to coordinator
        self.sendtocoordinator(new_message)

    def broadcastmessages(self):
        for client_id, message in self.MY_MESSAGES:
            print("%s: %s", client_id, message)

    def newclient(self):
        #TODO, decide on a naming scheme for client
        new_client = Client(str(self.MY_PORT) + str(random.randint(1, 100)))
        self.MY_CLIENTS[new_client.client_id] = new_client
        print("Server: Client {} created".format(new_client.client_id))
        data = dict()
        data['msg_type'] = 'CLIENT_JOIN'
        data['public_key'] = new_client.public_key
        self.sendtocoordinator(data)
        data['msg_type'] = 'NEW_WALLET'
        data['public_key'] = new_client.wallets[0]['public_key']
        self.sendtocoordinator(data)

    def shuffle(self, wallet_list, g, p, server_list):
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
        print("Here")
        for nym in nym_map:
            print("{0}: Reputation 1".format(nym))

    def vote(self, client_id, message_id, vote):
        if self.current_round != "VOTE_START":
            return
        # get message
        new_vote_msg = self.MY_CLIENTS[client_id].vote(message_id, vote, self.known_clients)
        if not util.LRSverify(new_vote_msg["msg_id"], self.known_clients, new_vote_msg["signature"]):
            print("Voting: LRS verify failed.")

        # lrs = util.LRSsign(signing_key, public_key_idx, message, self.known_clients) # (signing_key, public_key_idx, message, public_key_list)
        self.sendtocoordinator(new_vote_msg)

    def newvoteupdateledger(self, message): # this is the leader server updating the ledger
        new_block = self.MY_LEDGER.logvote(message["signature"], message["msg_id"], int(message['vote']))
        new_message = {
            'msg_type': "LEDGER_UPDATE",
            'new_block': new_block
        }
        self.sendtocoordinator(new_message)

    def mergeledger(self, message):
        self.MY_LEDGER.appendblock(message['new_block'])

    def newwalletupdateledger(self, message):
    # this is the leader server updating the ledger for new wallets created
        new_block = self.MY_LEDGER.lognewwallets(message['nym'], message['nym_sig'],
                                                message['new_wallet_public_keys'])
        new_message = {
            'msg_type': "LEDGER_UPDATE",
            'new_block': new_block
        }
        self.sendtocoordinator(new_message)

    def sendvotestoclients(self, vote_list):
        new_wallet_list = []
        for client_id in self.MY_CLIENTS:
            new_blocks, new_public_keys = self.MY_CLIENTS[client_id].recalculateWallets(vote_list, self.CURRENT_GEN_POWERED)
            new_wallet_list.extend(new_public_keys)
            # append transactions to ledger
            for new_block in new_blocks:
                new_block["msg_type"] = "WALLET_BLOCK"
                self.sendtocoordinator(new_block)

        return new_wallet_list

    def returnvotecount(self, message):
        new_message = {
            'msg_type': "VOTE_COUNT",
            'dict': self.MY_LEDGER.ALL_VOTES
        }
        self.sendtocoordinator(new_message)

    def serverjoin(self):
        mydict = dict()
        mydict['msg_type'] = 'SERVER_JOIN'
        self.sendtocoordinator(mydict)

    def showmessage(self, text, msg_id, nyms):
        print("ID: {0} Message: {1}. Signed by {2}".format(msg_id, text, nyms))

    def proofofwork(self, hash):
        salt = 0
