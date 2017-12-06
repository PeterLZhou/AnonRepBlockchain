import socket
import threading
from client import Client
from server import Server
import time
import json
import util

# phases
UNKNOWN = 99
SERVER_CONFIG = 0
READY_FOR_NEW_ROUND = 1
ANNOUNCE = 2
MESSAGE_SEND = 3
VOTE = 4
SPLIT = 5
REVERTNYM = 6

class Coordinator():

    def __init__(self, generator, modulus, ip, port):

        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_ip = ip
        self.my_port = port
        self.NEXT_PHASE = [SERVER_CONFIG, READY_FOR_NEW_ROUND, ANNOUNCE, MESSAGE_SEND, VOTE, SPLIT]
        self.current_phase_start = time.clock()

        self.gen = generator
        self.p = modulus
        self.known_servers = []
        self.pending_servers = []
        self.original_reputation_map = {}
        self.prev_original_reputation_map = {}
        self.known_client_pubkeys = []
        self.nym_map = {}
        self.final_generator = None
        self.aggregated_messages = []
        self.wallet_specific_messages = []
        self.round_votes = {}
        self.current_phase = SERVER_CONFIG
        self.connected = False
        # store highest reputation from last round, broadcast with READ_FOR_NEW_ROUND
        self.last_highest_rep = -1
        self.num_rounds = 0
        self.last_block = None

        try:
            self.receivesocket.bind((self.my_ip, self.my_port))
            print("Connected to port ", self.my_port)
            self.connected = True
        except:
            print("Port {} is probably in use".format(self.my_port))

    def startNextRound(self):

        # finish tasks before current phase ends

        self.current_phase = self.NEXT_PHASE[(self.current_phase + 1) % len(self.NEXT_PHASE)]

        if self.current_phase == SPLIT:
            # split phase begins here
            pm = {}
            pm['msg_type'] = "VOTE_END"
            for server_ip, server_port in self.known_servers:
                util.sendDict(pm, server_ip, server_port, self.receivesocket)

            leader_ip, leader_port = self.decideLeader()
            pm['msg_type'] = "GET_VOTE_COUNT"
            util.sendDict(pm, leader_ip, leader_port, self.receivesocket)

        # more phase handling code
        # most importantly, need to signal each server that new phase has begun
        # finish tasks before new phase starts
        if self.current_phase == VOTE:
            pm = {}
            pm['msg_type'] = "VOTE_START"
            for server_ip, server_port in self.known_servers:
                util.sendDict(pm, server_ip, server_port, self.receivesocket)
        elif self.current_phase == READY_FOR_NEW_ROUND:
            self.startShuffle()

    def startShuffle(self):

        # signal to first server to start shuffle phase
        if len(self.known_servers) == 0:
            return

        pm = {}
        pm["msg_type"] = "SHUFFLE"
        pm["wallet_list"] = self.original_reputation_map
        pm["g"] = self.gen
        pm["p"] = self.p
        pm["server_list"] = self.known_servers

        print("Starting shuffle...")

        server_ip, server_port = self.known_servers[0]
        util.sendDict(pm, server_ip, server_port, self.receivesocket)

    def handleMessage(self, message_dict):

        new_aggr_msg = {}
        new_aggr_msg["text"] = message_dict["text_msg"]
        new_aggr_msg["signature"] = message_dict["signatures"] # change later
        new_aggr_msg["nyms"] = message_dict["pseudonyms"] # actually the public keys
        new_aggr_msg["id"] = len(self.aggregated_messages) + 1


        print("Message from", new_aggr_msg["nyms"])
        # verify signature (and send reply? don't think we need this here)

        self.aggregated_messages.append(new_aggr_msg)
        for server_ip, server_port in self.known_servers:
            pm = new_aggr_msg
            pm["msg_type"] = "MESSAGE_BROADCAST"
            util.sendDict(pm, server_ip, server_port, self.receivesocket)
        return

    # def handleMessageBroadcast(self):
    #
    #     # aggregate all messages with same text, this is a very stupid way to
    #     # do this currently
    #     if len(self.wallet_specific_messages) == 0:
    #         return
    #
    #     sorted_messages = sorted(self.wallet_specific_messages, key=lambda k: k['text'])
    #     new_aggr_message = {}
    #     new_aggr_message['text'] = sorted_messages[0]['text']
    #     new_aggr_message['id'] = len(self.aggregated_messages) + 1
    #     new_aggr_message['nyms'] = [sorted_messages[0]['nym']] # do we need to store signatures? unclear
    #
    #     for wallet_msg in sorted_messages:
    #         if wallet_msg['text'] == new_aggr_message['text']:
    #             new_aggr_message['nyms'].append(wallet_msg['nym'])
    #         else:
    #             self.aggregated_messages.append(new_aggr_message)
    #             new_aggr_message['text'] = wallet_msg['text']
    #             new_aggr_message['id'] = len(self.aggregated_messages) + 1
    #             new_aggr_message['nyms'] = [wallet_msg['nym']]
    #
    #     self.aggregated_messages.append(new_aggr_message)
    #
    #     # broadcast all messages to each server
    #     for server_ip, server_port in self.known_servers:
    #         for message in self.aggregated_messages:
    #             pm = message
    #             pm["msg_type"] = "MESSAGE_BROADCAST"
    #             util.sendDict(pm, server_ip, server_port, self.receivesocket)

    def decideLeader(self):

        return self.known_servers[0]

    def handleWalletBlock(self, wallet_block_dict):

        wallet_block_dict["msg_type"] = "NEW_WALLET"
        leader_ip, leader_port = self.decideLeader()

        util.sendDict(wallet_block_dict, leader_ip, leader_port, self.receivesocket)

    def handleVote(self, vote_dict):

        msg_id = vote_dict["msg_id"]
        vote = int(vote_dict["vote"])
        lrs = vote_dict["signature"]

        print("Received vote", vote, "for message", msg_id)

        if(len(self.aggregated_messages) < int(msg_id) or (vote != -1 and vote != 1)):
            # invalid vote, send reply saying this
            print("Invalid vote {0} for {1} received".format(vote, msg_id))
            return
        else:
            vote_dict["msg_type"] = "NEW_VOTE"

            if msg_id in self.round_votes:
                self.round_votes[msg_id]  += vote
            else:
                self.round_votes[msg_id] = vote

            leader_ip, leader_port = self.decideLeader()
            util.sendDict(vote_dict, leader_ip, leader_port, self.receivesocket)

    # When voting phase is over, blockchain contains a list of transactions
    # that determine how many votes a message received. Aggregate them and broadcast
    # to all servers
    def aggregateVotes(self, vote_dict):

        aggr_votes = vote_dict["dict"]
        vote_per_wallet = {}

        for msg in self.aggregated_messages:
            if str(msg["id"]) in aggr_votes:
                total_votes = aggr_votes[str(msg["id"])]
                num_nyms = len(msg["nyms"])

                for (idx, nym) in enumerate(msg["nyms"]):
                    wallet_rep = int(total_votes / (num_nyms - idx))
                    if wallet_rep < -2:
                        wallet_rep = -2
                    total_votes = total_votes - wallet_rep
                    if nym in vote_per_wallet:
                        vote_per_wallet[nym] = max(-2, vote_per_wallet[nym] + wallet_rep)
                    else:
                        vote_per_wallet[nym] = wallet_rep

        for nym in self.nym_map:
            if nym in vote_per_wallet:
                vote_per_wallet[nym] += 1
            else:
                vote_per_wallet[nym] = 1

        pm = {
            "msg_type": "VOTE_RESULT",
            "wallet_delta": vote_per_wallet
        }

        # forget old pseudonyms
        self.prev_original_reputation_map = self.original_reputation_map
        self.original_reputation_map = {}

        for (server_ip, server_port) in self.known_servers:
            util.sendDict(pm, server_ip, server_port, self.receivesocket)

        # for (idx, msg) in enumerate(self.aggregated_messages):
        #     msg_votes = util.aggregateBlockchain(blockchain, msg["id"])
        #     self.round_votes[msg_id] = min(msg_votes, -len(msg["nyms"]))
        #     msg["votes"] = self.round_votes[msg_id]
        #     self.aggregated_messages[idx] = msg
        #
        # for (server_ip, server_port) in self.known_servers:
        #     pm = {}
        #     pm["msg_type"] = "VOTE_RESULT"
        #     pm["votes"] = self.aggregated_messages
        #     util.sendDict(pm, server_ip, server_port, self.receivesocket)

    def registerNewWallet(self, wallet_dict):

        wallet_pub_key = wallet_dict["public_key"]

        # do error checking to see if sender was allowed to send this wallet
        self.original_reputation_map[wallet_pub_key] = 1
        print("Registered new wallet", wallet_pub_key)

    def handleClientJoin(self, client_dict):

        if "public_key" in client_dict:
            client_pub_key = client_dict["public_key"]
            self.known_client_pubkeys.append(client_pub_key)

        print("Registered new client", client_pub_key)


    def handleServerJoin(self, server_ip, server_port):
        pm = {}
        next_hop_msg = {}
        pm["msg_type"] = "SERVER_JOIN_REPLY"
        pm["status"] = "SUCCESS"
        for known_ip, known_port in self.known_servers:
            if known_ip == server_ip and known_port == server_port:
                pm["status"] = "INVALID"
                util.sendDict(pm, server_ip, server_port, self.receivesocket)
                return

        self.known_servers.append((server_ip, server_port))
        if len(self.known_servers) > 1:
            pm["prev_hop_ip"], pm["prev_hop_port"] = self.known_servers[-2]

            next_hop_msg["msg_type"] = "SERVER_NEXT_HOP_UPDATE"
            pm["next_hop_ip"], pm["next_hop_port"] = self.known_servers[-1]
            prev_ip, prev_port = self.known_servers[-2]

            util.sendDict(next_hop_msg, prev_ip, prev_port, self.receivesocket)


        util.sendDict(pm, server_ip, server_port, self.receivesocket)
        print("New server joined: " ,server_ip, server_port)

    # handle the results of shuffle phase from last server
    def handleAnnouncement(self, announce_dict):

        print("Announcing nyms")
        print(announce_dict["wallet_list"])

        self.nym_map = announce_dict["wallet_list"]
        self.final_generator = announce_dict["g"]
        pm = {}
        pm["nym_map"] = self.nym_map
        pm["msg_type"] = "NYM_ANNOUNCE"
        pm["gen_powered"] = self.final_generator
        pm["g"] = self.gen
        pm["p"] = self.p

        for (ip, port) in self.known_servers:
            util.sendDict(pm, ip, port, self.receivesocket)

        # broadcast client public keys
        pm = {}
        pm["client_pubkeys"] = self.known_client_pubkeys
        pm["msg_type"] = "CLIENT_ANNOUNCE"

        for (ip, port) in self.known_servers:
            util.sendDict(pm, ip, port, self.receivesocket)

        self.startNextRound()

    def broadcastLedger(self, ledger_dict, sender_ip, sender_port):
        for (ip, port) in self.known_servers:
            if not (ip == sender_ip and port == sender_port):
                util.sendDict(ledger_dict, ip, port, self.receivesocket)


    def listenAndCoordinate(self):

        # while True:
        #     time_now = time.clock()
        #     if(time_now - self.current_phase_start > phase_duration):
        #         self.startNextRound()

        # read datagram if any
        # @Peter: I need a readData method that reads a dictionary, returning
        # None if no data is received within `timeout` seconds. Serialize the
        # data using json to send and received dicts
        while True:
            data, addr = self.receivesocket.recvfrom(1000000)
            new_data = util.readDict(data)
            sender_ip, sender_port = addr
            if not new_data:
                continue

            # handle the message
            if new_data['msg_type'] == "SERVER_JOIN":
                self.handleServerJoin(sender_ip, sender_port)
            elif new_data['msg_type'] == "CLIENT_JOIN":
                self.handleClientJoin(new_data)
            elif new_data['msg_type'] == "MESSAGE":
                self.handleMessage(new_data)
            elif new_data['msg_type'] == "VOTE":
                self.handleVote(new_data)
            elif new_data['msg_type'] == "NEW_WALLET":
                if self.current_phase != SERVER_CONFIG:
                    continue
                self.registerNewWallet(new_data)
            elif new_data['msg_type'] == "SHUFFLE_END":
                if self.current_phase != READY_FOR_NEW_ROUND:
                    continue
                self.startNextRound()
                self.handleAnnouncement(new_data)
            elif new_data['msg_type'] == "LEDGER_UPDATE":
                if self.current_phase != VOTE:
                    continue
                self.broadcastLedger(new_data, sender_ip, sender_port)
            elif new_data['msg_type'] == "VOTE_COUNT":
                if self.current_phase != SPLIT:
                    continue
                self.aggregateVotes(new_data)
            elif new_data['msg_type'] == "WALLET_BLOCK":
                if self.current_phase != SPLIT:
                    continue
                self.handleWalletBlock(new_data)
