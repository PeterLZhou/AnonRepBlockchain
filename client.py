import socket
import threading
import uuid
import util
from random import *
from ledger import Ledger

class Client():
    def __init__(self, client_id):
        # I imagined wallets to be a list of dictionaries and each dictionary would have the following:
        # {
        #    "private_key": the key that will be used to sign new messages
        #    "public_key": the public key of the wallet
        #    "Reputation": the amount of reputation that the wallet has << all wallets have only one reputation, so this is unncessary
        # maybe we want to add another item in here for the wallet's identity
        # }
        self.wallets = []

        # start with 1 wallet with reputation=1 (feel free to change this)
        first_wallet = self.createwallet()
        # maybe we want to publish to the ledger? it's not an important issue, but we want to make sure that we can't just create random wallets out of nowhere
        self.wallets.append(first_wallet)

        # Client ID is just the ID of the port it's on, since we only have 1 client/port
        # Long standing private key
        # I think we're going to need a list of private keys that correspond to the individual wallets
        # ^that should be taken care of by self.wallets 
        self.client_id = client_id
        self.private_key = util.generatePrivateKey()
        self.public_key = util.generatePublicKey(self.private_key)

        self.threshold = 1 # the maximum amount of reputation a wallet is allowed to have

        self.my_ledger = Ledger()
        print("Client ID: ", self.client_id)
        print("Client public key: ", self.public_key)
        print("Client private key: ", self.private_key)

    # Called by the server, returns a list of new wallets
    # the private keys will be kept by the client, but the public keys will be shared with the server
    def split(self, walletid):

        # I'm assuming that walletid is the oldwallet that needs to be split
        # maybe we should be looping through all the wallets that the client has and calling a split on all of them
        oldwallet = None #TODO @Eugine - once you figure createwallet out find out how to get the wallet by reference
        new_wallets = []

        # do some kind of signing with the privatekey of the oldwallet
        signed_oldwallet = oldwallet["private_key"] # we obviously do NOT want to send the private key
        while oldwallet['Reputation'] > self.threshold:
            newwallet = self.createwallet()
            # TODO: Split currency among the new wallets

            # transfer threshold reputation points from oldwallet to newwallet
            self.my_ledger.send_reputation(signed_oldwallet, newwallet["public_key"], self.threshold)
            # make sure that the server is publishing/broadcasting the new updated ledger with this change
            newwallet["Reputation"] += self.threshold
            new_wallets.append(newwallet)

        return new_wallets

    # Adds the wallet to the dictionary. Returns the key for the wallet in the dict
    def createwallet(self):
        keys = util.generateWalletKeys()
        private_key = keys['privateKey'].x
        public_key = keys['publicKey'].h
        reputation = 1

        wallet = {
            "private_key": private_key,
            "public_key": public_key,
        }
        return wallet

    def generate_signed_messages(self, message_text):
        # TODO: get last_highest_rep from coordinator and choose amount of reputation to use
        # may not be necessary anymore
        signed_messages = []

        # currently use all reputation
        for wallet in self.wallets:
            message_dict = {
                "text": message_text,
                "signature": wallet["public_key"]
                # TODO: not sure we need to add a nym here? isn't the signature sufficient?
                #"nym" =
            }
            signed_messages.append(message_dict)
        return signed_messages
