1.) Members and the division of work:
Dibyatanoy Bhattacharjee: Did most of the coordinator code and server code
Peter Zhou: Did some of the client and server code, most of the crypto functions, and the README
Kristina Shia: Wrote utility functions, did the slides, and added crypto libraries, organized everything and directed members
Eugine Szeto: Wrote most of the ledger and blockchain implementation contained in both the server and client code and some of the server code

2.) Our system is called BlockRep and is a blockchain-based approach to AnonRep, aimed at solving the problem of intersection attacks (being able to track a one-time pseudonym across multiple rounds of voting). To do this, BlockRep splits every user's reputation into discrete units called wallets, each containing a public W_P and private W_p. Every client contains access to multiple wallets and contains one long-standing public key C_P and one long-standing private key C_p. There are multiple phases inside of BlockRep, described below:

SERVER_CONFIG/READY_FOR_NEW_ROUND:
All servers and their corresponding clients connect to the coordinator. The clients also share their wallet public keys to the coordinator. At the end of the phase, the coordinator sends to all servers a list containing all client public keys and all wallet public keys existing in the current round. In the implementation, you must start up the coordinator before trying to connect as a server. Running "python coordinator_launch.py" starts the coordinator, and running "python anonrep.py" starts a server. Once the server has connected, you should see a "Server join status:  SUCCESS" on the interface of the server. To move on to the next phase, type "next_round" and hit return on the coordinator_launch's terminal.

ANNOUNCE:
The coordinator, who contains all wallet public keys, decides on a shuffling route using the existing servers. In this phase, each server applies a layer of encryption on the list of wallet public keys and a generator, and then passes it along to the next server. The final server to apply the layer of encryption sends the list of completed pseudonyms to the coordinator. The coordinator broadcasts the pseudonym list and exponentiated generator to everyone. In order to encrypt the pseudonyms, each server generates a random number r, and has knowledge of global variables P and G. Every wallet's private key is X, and every wallet's public key is G^X. Each server raises every member of the incomplete pseudonym list to the power of their random number, modding with P after. Thus, at the end, the final pseudonym list contains pseudonyms of the form "G^(r1 * r2 * r3... * X)", and the compounded generator contains the form "G^(r1 * r2 * r3)". In order for a client to verify that their pseudonym exists, they take the compounded generator "G^(r1 * r2 * r3)" and raise that to their private key, which they confirm to be equal to one of the pseudonyms in the list. After this, the message posting phase begins.

MESSAGE_SEND:
Once everyone has received pseudonyms for everyone else, Clients are given the option to send messages by typing "pm <client_id> <reputation> <message>" in the anonrep.py terminal. This causes the client to create a string called "message", select <reputation> amount of wallets, and then sign the message with each wallet using an elgamal signature (which can be found in util.py). The client passes along a dictionary containing message, public keys of each wallet used to sign the message, and the corresponding signatures of each message. The server verifies that each signature is correct by using the elgamal verification scheme, then sends the message to the coordinator, who indexes the message and broadcasts it to everyone. This should show up on every server’s anonrep.py as "ID: {0} Message: {1}. Signed by {2}", where 0 is the message index, 1 is the message, and 2 is the list of wallet public keys. Clients are allowed to write as many messages as they want, but may not write messages using more reputation than the total amount of wallets they have. Once everyone is done sending messages, type next_round to move to the next phase.

VOTE:
In the voting phase, clients may vote on a message by typing in anonrep.py “upvote <client_id> <message_idx>” or “downvote <client_id> <message_idx”. This will generate a linkable ring signature using the client’s private key and all known public keys. The linkable ring signature is then verified by the server before being passed along to the coordinator. The coordinator aggregates a list of wallet pseudonyms and amount of reputation they should have for the next round (this should be anywhere from 0 to infinity). In order to maintain a log of transactions used for verification, every server stores a ledger which contains a blockchain. Every time a client decides to vote on a message, the server that the client is hosted on will create a block based on that vote. The server will then send the newly created block to the coordinator. Then, the coordinator decides on a leader (which is some server) to send the new block to. From there, the leader adds the block to the blockchain by generating a salt for the new block. In addition, the leader will also keep a running total of the msg_id’s and their respective votes. The salt and the previous block’s hash of the new block are included in the new block that the leader has just created. That new block the leader has created will be sent to the coordinator, who will then broadcast that new block to all the servers. All the servers will then add the new block to their own ledgers.

SPLIT:
When we need to create new wallets after the voting phase, the coordinator will signal to the lead server, which will return a dictionary of wallet pseudonyms and their respective votes. Upon that signal from the coordinator, the servers pass the mapping of wallet pseudonyms and votes to the clients and the clients iterate through the mapping, creating new wallets for each wallet involved in the message posting phase. The clients will keep the private keys of the new wallets to themselves, but they will return to the servers the public keys of the wallets, which the servers will pass to the coordinator the end the split phase and start all over again from the SERVER_CONFIG/READY_FOR_NEW_ROUND phase. In order to assure that the clients are honest in their creation of new wallets, they will create a block to append to the blockchain that shows a transaction from their old wallet pseudonym to the corresponding new wallets. This transaction is elgamal signed using the old wallet’s private key as well to ensure that only the owner of the old wallet can break it up to create new wallets.
Relating to the implementation, the client runs as its own class on top of the server - we separate the two by ensuring that the server never accesses a private member of the client’s, and calls client functions for things the client should do (such as generating the linkable ring signature). The server and coordinator are both multithreaded applications - one thread continuously calls listen to await socket connections and messages through those connections, and the other thread awaits user command line input to allow switching of phases by the coordinator and sending / voting of messages by the clients. The user input parsing as well as the multithreaded implementations can be found inside of coordinator_launch.py and anonrep.py. The implementation for all the functions of the coordinator can be found inside of coordinator.py. The implementation for all the functions of the server and client can be found inside of server.py and client.py respectively. We send all messages through UDP sockets, and attach a ‘msg_type’ to each message to that the server/coordinator can react accordingly. Additionally, there are many cryptographic schemes we’ve either implemented or taken from open-sourced code (with proper attribution). These can be found inside of util.py, as well as our functions for sending dictionaries over UDP sockets.


3.) In this example, the user should have four terminals open at the same time. I will denote what gets typed in each terminal by prefixing with [1...4] >. Here are a set of instructions that will simulate a voting round.

Before starting, download all requirements with “pip install -r requirements.txt”

[1] > python coordinator_launch.py
# Starts coordinator
[2] > python anonrep.py
[3] > python anonrep.py
[4] > python anonrep.py
# Starts the three servers. By default, each server creates its own client, so there are three clients in our system.
[1] > next_round
# Starts the announcement round, then moves directly into the message posting round. Now, every client has a list of wallet pseudonyms and can post messages
[2] > pm <client_id> 1 helloworld
[3] > pm <client_id> 1 goodbyeworld
# Posts two messages using the client living on server 1 and the client living on server 2. Immediately after posting, every server should see the messages appear on their screen. The message posted by server 1 should have index 1 and the message posted by server 2 should have index 2.
[1] > next_round
# The coordinator decides the message posting round is over and begins the voting round, allowing everyone to vote on messages.
[4] upvote <client_id> 1
# Here, the client hosted on server 3 gives message 1 (which was posted by the client on server 1) a positive vote. This vote is also added to the blockchain maintained by everybody, which is maintained under the hood.
[1] > next_round
# The coordinator decides voting is over, and sends every server a list of pseudonyms mapped to how many reputation points they should have. The coordinator immediately begins the next round, moving straight to the SERVER_CONFIG/READY_FOR_NEW_ROUND phase. During this time, the servers pass the list to each of their clients, who examine each wallet pseudonym to find their own wallets and create a number of wallets equal to the amount of reputation they should currently have. The clients return the public keys associated with these new wallets and the server sends them to the coordinator, who rebroadcasts the new public keys list to every server. This concludes the round and starts the next message posting round - notice that now there is one additional wallet pseudonym, because the client on server 1 has one additional wallet.


Example Run:

COORDINATOR:

>python3 coordinator_launch.py

Connected to port  5003

*** Server Config Phase ***

# New server joins
New server joined:  127.0.0.1 5000

# New client joins on this server
Registered new client (109919412191312255827829364441244210716145930774987630887297061308035523576901,27398101575023247282354285655558820038450292375928628928145581720155853449217)

# Every client starts off with one wallet
Registered new wallet 48144504382147390689047348990905902013784874470918825434868028864736745205167

# Another server joins
New server joined:  127.0.0.1 5001
Registered new client (37928780378350448111920417685670705257653121305339731256087820737082564220271,14922184807129824658986997840373595274871621573222204418596621454415873096894)
Registered new wallet 41172708402787218699572580635999400893366210593482922115341188810867605632433
Registered new client (86136417583735705194854398153048832645162590138513001183721620402457401381007,51907681114700528130734434473096331082483422658371017829764918285149333604361)
Registered new wallet 20024771758216321785377506748846435837462712155939267677727044767743707928962
next_round

*** Starting shuffle... ***


*** Announcing nyms ***

next_round

*** Starting voting phase ***

Received vote 1 for message 1
Received vote 1 for message 2
Received vote 1 for message 2
next_round
Registered new wallet 12800780024125477634452061536829584481600951437116797769311710514323446251569
Registered new wallet 62076446159922720756962824110086482457252490382440909563000594587297050838525
Registered new wallet 5740030045454289375108785319078057683413737335830590548150116483706671771281
Registered new wallet 57367138011908978488920398513053054347459280625982833001701543235474401044587
Registered new wallet 24366175890837059710670749587993092780118901491973781571093469955488603804400
Registered new wallet 48150719694406226672044119219186382360892487355001478706745216026035364947522
next_round

*** Server Config Phase ***

next_round

*** Starting shuffle... ***

*** Announcing nyms ***



4.) CHALLENGES - A lot of the difficulty was understanding the entire system. The questions that we struggled with are as follows. How do we make sure the reputations after the voting phase are correctly given to the clients? In other words, how do we generate new wallets? How do we use blockchain appropriately in our system?

Beyond just understanding the system, we also had to figure out what parts we could reasonably simplify. One of the simplifications we struggled with was blockchain. For one, we simplified the mining process, which was an obvious choice to save time, especially because we chose to use Python.

In addition to understanding the architecture of the system, we struggled with finding the right libraries to meet all our needs, especially for the crypto parts of the project. Some of the libraries did not exist, and thus we had to implement the cryptographic primitives ourselves (a list of our cryptographic implementations can be found inside of util.py)
