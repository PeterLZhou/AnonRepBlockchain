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

#Sends dict as serialized data
def sendDict(data, ip_addr, port, sendsocket):
    serializeddict = serialize(data)
    sendsocket.sendto(serializeddict, (ip_addr, port))

#Returns clean dictionary
def readDict(data):
    return util.deserialize(data)

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
