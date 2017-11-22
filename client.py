import socket
import threading
import uuid
from random import *

class Client():
    def __init__(self, clientid):
        self.wallets = dict()
        # Client ID is just the ID of the port it's on, since we only have 1 client/port
        self.client_id = clientid
        # Long standing private key
        self.private_key = uuid.uuid4().hex

    # Called by the server, returns a tuple of two new public keys for the wallet
    def split(self, walletid):
        oldwallet = None #TODO @Eugine - once you figure createwallet out find out how to get the wallet by reference
        newwallet1 = self.createwallet()
        newwallet2 = self.createwallet()
        # TODO: Split currency among the new wallets
        del wallets[oldwallet]
        return (newwallet1, newwallet2)

    # Adds the wallet to the dictionary. Returns the key for the wallet in the dict
    def createwallet(self):
        # TODO @Eugine: Add in crypto code for initializing wallets - the way I
        # imagined it was a mapping of either publickey/privatekey/address to currency amt
        print("Not implemented")
