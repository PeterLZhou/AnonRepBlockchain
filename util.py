import socket
import threading
from client import Client
import time
import json
import util
import pickle
from linkable_ring_signature import ring_signature, verify_ring_signature
from ecdsa.util import randrange
from ecdsa.curves import SECP256k1

def sendDict(dict, ip_addr, port):
    print("Not implemented yet.")
    return

def readDict(timeout = 0.5):
    print("Not implemented yet.")
    # return dictionary_read, sender_ip, sender_port

def serialize(obj):
	return pickle.dumps(obj)

def deserialize(string):
	return pickle.loads(string)

def LRSsign(signing_key, public_key_idx, message, public_key_list):

    signature = ring_signature(signing_key, public_key_idx, message, public_key_list)
    return signature

def LRSverify(message, public_key_list, signature):
    return verify_ring_signature(message, public_key_list, *signature)

def generatePrivateKey():
    return randrange(SECP256k1.order)

def generatePublicKey(private_key):
    return SECP256k1.generator * private_key

if __name__ == "__main__":
    ### TEST FOR LRS SIGN ###
    number_participants = 10

    x = [ randrange(SECP256k1.order) for i in range(number_participants)]
    y = list(map(lambda xi: SECP256k1.generator * xi, x))

    message = "Every move we made was a kiss"

    i = 2
    signature = LRSsign(x[i], i, message, y)
    print(LRSverify(message, y, signature))

    private_key = generatePrivateKey()
    public_key = generatePublicKey(private_key)
    print(private_key)
    print(public_key)
