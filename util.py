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

P = 78259045243861432232475255071584746141480579030179831349765025070491917900839
G = 850814731652311369604857817867299164248640829807806264080080192664697908283

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
    return int(hashlib.sha256(key).hexdigest(), 16)

def elgamalsign(message, private_key, gen_powered, P):
    k = 10**9 + 7
    r = modexp(gen_powered, k, P-1)
    s = modexp(modexp(sha256hash(message) - private_key * r), 1, P-1) * modinv(k, P-1), 1, P-1)
    return (r, s)

def elgamalverify(message, pseudonym, r, s, gen_powered, P):
    return modexp(gen_powered, sha256(message), P) == modexp(modexp(psuedonym, r, P) * modexp(r, s, P), 1, P)

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b%a,a)
    return (g, x - (b//a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('No modular inverse')
    return x%m

e = 17
d = modinv(e, k)

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

    message = "Hi"
