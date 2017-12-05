import socket
import threading
import uuid
import util
from random import *
from ledger import Ledger

P = 78259045243861432232475255071584746141480579030179831349765025070491917900839
G = 850814731652311369604857817867299164248640829807806264080080192664697908283

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

        self.my_ledger = Ledger()
        print("Client ID: ", self.client_id)
        print("Client public key: ", self.public_key)
        print("Client private key: ", self.private_key)

    # Called by the server, returns a list of new wallets
    # the private keys will be kept by the client, but the public keys will be shared with the server
    def recalculateWallets(self, vote_list, gen_powered):
        prev_reputation = len(self.wallets)
        for item in vote_list:
            owner = False
            for nym in nym_list:
                if owner:
                    break
                for wallet in wallet:
                    if verify_nym(wallet, nym, gen_powered):
                        owner = True
                        break
            if owner:
                prev_reputation += item['votes']
        new_wallet_list = []
        new_public_keys_list = []
        for i in range(prev_reputation):
            new_wallet = self.createwallet()
            new_wallet_list.append(new_wallet)
            new_public_keys_list.append(new_wallet['public_key'])
        self.wallets = new_wallet_list
        return new_public_keys_list




    def verify_nym(wallet, nym, gen_powered):
        return util.modexp(gen_powered, wallet['private_key'], P) == nym

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
