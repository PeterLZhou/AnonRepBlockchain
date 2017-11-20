TO RUN:

python anonrep.py

This starts two thread - a server thread which handles all the functionality, and a user thread which accepts user input
The command 'sendall' sends a UDP message to all other available servers (we assume localhost 5000, 5001, and 5002 are our server locations)
