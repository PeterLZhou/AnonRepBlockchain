import socket
import threading
from client import Client
import time
import json
import util
import pickle

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
