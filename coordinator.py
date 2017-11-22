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
MESSAGE = 3
VOTE = 4
SPLIT = 5

class Coordinator():

    def __init__(self, generator, modulus, ip, port):

        self.sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_ip = ip
        self.my_port = port
        self.NEXT_PHASE = [SERVER_CONFIG, READY_FOR_NEW_ROUND, ANNOUNCE, MESSAGE, VOTE]
        self.current_phase_start = time.clock()

        self.gen = g
        self.p = modulus
        self.known_servers = []
        self.pending_servers = []
        self.original_reputation_map = {}
        self.nym_map = {}
        self.final_generator = None
        self.messages = []
        self.round_votes = []
        self.current_phase = READY_FOR_NEW_ROUND
        self.connected = False

        try:
            self.receivesocket.bind((self.my_ip, self.my_port))
            print("Connected to port ", self.my_port)
            self.connected = True
        except:
            print("Port {} is probably in use".format(self.my_port))

    def startNextRound(self):

        self.current_phase = self.NEXT_PHASE[(self.current_phase + 1) % len(self.NEXT_PHASE)]
        # more phase handling code
        # most importantly, need to signal each server that new phase has begun

    def handleVote(self, vote_dict):

        vote_text = vote_dict["text"]
        sig = vote_dict["signature"]
        sender_nym = vote_dict["nym"]

        # check if duplicate vote using linkable ring signature

        commands = vote_text.split()
        msg_id = int(commands[0])
        vote = int(commands[1])

        if(len(messages) < msg_id or (vote != -1 and vote != 1)):
            # invalid vote, send reply saying this
            print("Invalid vote {0} for {1} received from {2}".format(vote, msg_id, sender_nym))
            return
        else:
            poster_nym = messages[msg_id-1]["nym"]
            self.nym_map[poster_nym] += vote


    def listenAndCoordinate(self, phase_duration=5.0, timeout=0.1):

        while True:
            time_now = time.clock()
            if(time_now - self.current_phase_start > phase_duration):
                self.startNextRound()

        # read datagram if any
        # @Peter: I need a readData method that reads a dictionary, returning
        # None if no data is received within `timeout` seconds. Serialize the
        # data using json to send and received dicts
        new_data = util.readData(timeout=0.1)
        if not new_data:
            continue

        # handle the message
        if new_data['msg_type'] == "SERVER_JOIN":
            pass
        elif new_data['msg_type'] == "NEW_MESSAGE":
            pass
        elif new_data['msg_type'] == "NEW_VOTE":
            pass
