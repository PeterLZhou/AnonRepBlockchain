import socket
import threading
import time
import json
import pickle
import elgamal
import hashlib
from linkable_ring_signature import ring_signature, verify_ring_signature
from ecdsa.util import randrange
from ecdsa.curves import SECP256k1

#Sends dict as serialized data
def sendDict(data, ip_addr, port, sendsocket):
    serializeddict = serialize(data)
    sendsocket.sendto(serializeddict, (ip_addr, port))

#Returns clean dictionary
def readDict(data):
    return deserialize(data)

def serialize(obj):
	return pickle.dumps(obj)

def deserialize(string):
	return pickle.loads(string)

def LRSsign(signing_key, public_key_idx, message, public_key_list):
    return ring_signature(signing_key, public_key_idx, message, public_key_list)

def LRSverify(message, public_key_list, signature):
    return verify_ring_signature(message, public_key_list, *signature)

def generatePrivateKey():
    return randrange(SECP256k1.order)

def generatePublicKey(private_key):
    return SECP256k1.generator * private_key

def modexp(base, exp, modulus):
	return pow(base, exp, modulus)

#Returns a dict {publicKey: ..., privateKey: ...,}
def generateWalletKeys():
    return elgamal.generate_keys()

def sha256hash(key):
    return hashlib.sha256(key).hexdigest()

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
    ### TEST FOR PUBLIC PRIVATE KEY ###
    pair = elgamal.generate_keys()
    print(pair)
    print(pair['privateKey'].p)
    print(pair['privateKey'].g)
    print(pair['privateKey'].x)
    pair2 = elgamal.generate_keys()
    print(pair2)
    print(pair2['privateKey'].p)
    print(pair2['privateKey'].g)
    print(pair2['privateKey'].x)

    cipher = elgamal.encrypt(pair['publicKey'], "This is the message I want to encrypt")
    print(cipher)
    plaintext = elgamal.decrypt(pair['privateKey'], cipher)
    print(plaintext)
