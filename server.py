import socket
import threading

#We hardcode all the available ports to make things easy
ALL_PORTS = [5000, 5001, 5002]

class Server():
    def __init__(self):
        # Used for the server to send outbound messages
        self.sendsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Used for the server to receive inbound messages
        self.receivesocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.MY_IP = "0.0.0.0"
        self.MY_PORT = 5000
        self.MESSAGES = []
        offset = 0
        connected = False
        while not connected:
            try:
                self.receivesocket.bind((self.MY_IP, self.MY_PORT))
                print("Connected to port ", self.MY_PORT)
                connected = True
            except:
                print("Port {} is probably in use".format(self.MY_PORT))
                self.MY_PORT += 1

    def listen(self):
        while True:
            data, addr = self.receivesocket.recvfrom(1024) # buffer size is 1024 bytes
            data = data.decode()
            self.MESSAGES.append(data)
            print("I got it: ", data)

    # Send a message to every port which is not yourself
    def sendall(self):
        message = "TEST MESSAGE"
        self.MESSAGES.append(message)
        for port in ALL_PORTS:
            if port != self.MY_PORT:
                self.sendsocket.sendto(message.encode(), (self.MY_IP, port))

    def dump(self):
        for message in self.MESSAGES:
            print(message)
