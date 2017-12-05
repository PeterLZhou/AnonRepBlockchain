
import socket
import threading
from server import Server
from client import Client

UDP_IP = 5000

my_server = Server()

threading1 = threading.Thread(target=my_server.listen)
threading1.daemon = True
threading1.start()

# User input
while True:
    try:
    	command = input("> ")
    except KeyboardInterrupt:
    	print("quitting")
    	quit()
    # Sends a message to every other server
    args = command.split()
    if args[0] == 'sendall':
        data = dict()
        data['msg_type'] = 'TEST'
        data['message'] = 'hi'
        my_server.sendall(data)
    elif args[0] == 'broadcast':
    	my_server.broadcastmessages()
    ### MESSAGING COMMANDS ###
    # postmessage <client_id (or one time pseudonym?)> <message (arbitrarily long with spaces)>
    elif args[0] == 'postmessage' or args[0] == 'pm':
        client_id = args[1]
        reputation = int(args[2])
        message = ' '.join(args[3:])
        my_server.postmessage(client_id, reputation, message)
    elif args[0] == 'dumpmessages':
        my_server.dumpmessages()
    ### VOTING COMMANDS ###
    # upvote/downvote <client_id> <message_id>
    elif args[0] == 'upvote':
        client_id = args[1]
        message_id = args[2]
        my_server.upvote(client_id, message_id)
    elif args[0] == 'downvote':
        client_id = args[1]
        message_id = args[2]
        my_server.downvote(client_id, message_id)
    elif args[0] == 'newclient':
        my_server.newclient()
