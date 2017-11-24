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
MESSAGE_BROADCAST = 4
VOTE = 5
SPLIT = 6
REVERTNYM = 7

class Coordinator():

    def __init__(self, generator, modulus, ip, port):

        self.sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_ip = ip
        self.my_port = port
        self.NEXT_PHASE = [SERVER_CONFIG, READY_FOR_NEW_ROUND, ANNOUNCE, MESSAGE_SEND, MESSAGE_BROADCAST, VOTE, REVERTNYM]
        self.current_phase_start = time.clock()

        self.gen = g
        self.p = modulus
        self.known_servers = []
        self.pending_servers = []
        self.original_reputation_map = {}
        self.nym_map = {}
        self.final_generator = None
        self.aggregated_messages = []
        self.wallet_specific_messages = []
        self.round_votes = {}
        self.current_phase = READY_FOR_NEW_ROUND
        self.connected = False
        # store highest reputation from last round, broadcast with READ_FOR_NEW_ROUND
        self.last_highest_rep = -1

        try:
            self.receivesocket.bind((self.my_ip, self.my_port))
            print("Connected to port ", self.my_port)
            self.connected = True
        except:
            print("Port {} is probably in use".format(self.my_port))

    def startNextRound(self):

        # finish tasks before current phase ends
        if self.current_phase == VOTE:
            # split phase begins here

        self.current_phase = self.NEXT_PHASE[(self.current_phase + 1) % len(self.NEXT_PHASE)]
        # more phase handling code
        # most importantly, need to signal each server that new phase has begun

        # finish tasks before new phase starts
        if self.current_phase == VOTE:
            pm = {}
            pm['msg_type'] = "VOTE_START"
            for server_ip, server_port in self.known_servers:
                util.sendDict(pm, server_ip, server_port)

    def handleMessage(self, message_dict):

        new_wallet_msg = {}
        new_wallet_msg["text"] = message_dict["text"]
        new_wallet_msg["signature"] = message_dict["signature"]
        new_wallet_msg["nym"] = message_dict["nym"]

        # verify signature (and send reply? don't think we need this here)

        self.wallet_specific_messages.append(new_wallet_msg)
        return

    def handleMessageBroadcast(self):

        # aggregate all messages with same text, this is a very stupid way to
        # do this currently
        if len(self.wallet_specific_messages) == 0:
            return

        sorted_messages = sorted(self.wallet_specific_messages, key=lambda k: k['text'])
        new_aggr_message = {}
        new_aggr_message['text'] = sorted_messages[0]['text']
        new_aggr_message['id'] = len(self.aggregated_messages) + 1
        new_aggr_message['nyms'] = [sorted_messages[0]['nym']] # do we need to store signatures? unclear

        for wallet_msg in sorted_messages:
            if wallet_msg['text'] == new_aggr_message['text']:
                new_aggr_message['nyms'].append(wallet_msg['nym'])
            else:
                self.aggregated_messages.append(new_aggr_message)
                new_aggr_message['text'] = wallet_msg['text']
                new_aggr_message['id'] = len(self.aggregated_messages) + 1
                new_aggr_message['nyms'] = [wallet_msg['nym']]

        self.aggregated_messages.append(new_aggr_message)

        # broadcast all messages to each server
        for server_ip, server_port in self.known_servers:
            for message in self.aggregated_messages:
                pm = message
                pm["msg_type"] = "MESSAGE_BROADCAST"
                util.sendDict(pm, server_ip, server_port)

    def handleVote(self, vote_dict):

        vote_text = vote_dict["text"]
        sig = vote_dict["signature"]
        sender_nym = vote_dict["nym"]

        # check if duplicate vote using linkable ring signature

        commands = vote_text.split()
        msg_id = int(commands[0])
        vote = int(commands[1])

        if(len(aggregated_messages) < msg_id or (vote != -1 and vote != 1)):
            # invalid vote, send reply saying this
            print("Invalid vote {0} for {1} received from {2}".format(vote, msg_id, sender_nym))
            return
        else:
            # store votes by message
            if msg_id in self.round_votes:
                self.round_votes[msg_id]  += vote
            else:
                self.round_votes[msg_id] = vote

    def handleServerJoin(self, server_ip, server_port):
        pm = {}
        next_hop_msg = {}
        pm["msg_type"] = "SERVER_JOIN_REPLY"
        pm["status"] = "SUCCESS"
        for known_ip, known_port in self.known_servers:
            if known_ip == server_ip and known_port == server_port:
                pm["status"] = "INVALID"
                util.sendDict(pm, server_ip, server_port)
                return

        if len(self.known_servers) > 0:
            pm["prev_hop_ip"], pm["prev_hop_port"] = self.known_servers[-1]
            self.known_servers.append((server_ip, server_port))

            next_hop_msg["msg_type"] = "SERVER_NEXT_HOP_UPDATE"
            pm["next_hop_ip"], pm["next_hop_port"] = self.known_servers[-1]
            prev_ip, prev_port = self.known_servers[-2]

            util.sendDict(next_hop_msg, prev_ip, prev_port)

        util.sendDict(pm, server_ip, server_port)

    def listenAndCoordinate(self, phase_duration=5.0, timeout=0.1):

        while True:
            time_now = time.clock()
            if(time_now - self.current_phase_start > phase_duration):
                self.startNextRound()

        # read datagram if any
        # @Peter: I need a readData method that reads a dictionary, returning
        # None if no data is received within `timeout` seconds. Serialize the
        # data using json to send and received dicts
        new_data, sender_ip, sender_port = util.readDict(timeout=0.1)
        if not new_data:
            continue

        # handle the message
        if new_data['msg_type'] == "SERVER_JOIN":
            handleServerJoin(sender_ip, sender_port)
        elif new_data['msg_type'] == "NEW_MESSAGE":
            pass
        elif new_data['msg_type'] == "NEW_VOTE":
            handleVote(new_data)
