import util

class Ledger:
    def __init__(self):
        # each block is a dictionary as follows:
        '''
        For a vote:
            {
                "link_ring_sig": linkable-ring-signature of the client making the upvote
                "msg_id": message id of the message that is being voted on
                "vote": the vote that is being given to the message wth the msg_id
                "salt": the salt that verifies the block has not be tampered with
                            salt is none if the block is in the awaiting list
                "prev_block": hash of the previous block
            }

        For a wallet:
        {
            "nym": pseudonym of the wallet that generated these wallets,
            "nym_sig": signature that verifies the identity of the nym,
            "new_wallet_public_keys": new_wallet_public_keys,
            "prev_block": hash of the previous block
        }
        '''

        self.BLOCKS = {}
        self.TAIL_BLOCK = "-1" # default starting block hash value
        self.BLOCKS[self.TAIL_BLOCK] = -1
        self.ALL_VOTES = {}
        # ALL_VOTES will be an aggregate of all the votes on the messages and will be a dict as follows:
        '''
            {
                "msg_id": vote_count
            }
        '''
    def resetvotes(self):
        self.ALL_VOTES = {}

    def appendblock(self, new_block):
        # insert optional verification
        new_block_hash = util.sha256hash(str(new_block).encode('utf-8'))
        self.BLOCKS[new_block_hash] = new_block
        self.TAIL_BLOCK = new_block_hash
        if 'msg_id' in new_block and 'vote' in new_block:
            self.updatevotes(new_block['msg_id'], new_block['vote'])

    def lognewwallets(self, nym, nym_sig, new_wallet_public_keys):
        '''processing new wallets, should only be called by lead server
        '''
        new_block = {
            "nym": nym,
            "nym_sig": nym_sig,
            "new_wallet_public_keys": new_wallet_public_keys,
            "prev_block": self.TAIL_BLOCK
        }
        salt = self.signblock(new_block)
        new_block['salt'] = salt
        self.appendblock(new_block)
        return new_block

    def logvote(self, link_ring_sig, msg_id, vote):
        '''processing a vote, should only be called by lead server
        '''
        new_block = {
            "link_ring_sig": link_ring_sig,
            "msg_id": msg_id,
            "vote": vote,
            "prev_block": self.TAIL_BLOCK
        }
        salt = self.signblock(new_block)
        new_block['salt'] = salt
        self.appendblock(new_block)
        return new_block

    def signblock(self, new_block):
        '''
            should be called by the server so that the results can be broadcasted
            We can make this signing as easy as possible
        '''
        salt = None
        prev_char = ""
        count = 0
        valid_salt = False
        while True:
            if count > 1114112:
                prev_char += chr(0)
                count = 0
            salt = prev_char + chr(count)
            if self.verifysignature(self.TAIL_BLOCK, salt):
                break
            count += 1

        return salt

    def verifysignature(self, prev_hash, salt):
        '''We can make this crypto as easy or as difficult as we want
        is valid if last digit of hash is less or equal to 3 (increase this to make faster)
        '''
        result = util.sha256hash((str(prev_hash) + salt).encode('utf-8'))
        if result % 10 <= 3:
            return True
        else:
            return False

    def auditblocks(self):
        current_block = self.BLOCKS[self.TAIL_BLOCK]
        while current_block != -1: # while not at tail
            if not self.verifysignature(current_block['prev_hash'], current_block['salt']):
                return False
            else:
                current_block = self.BLOCKS[current_block['prev_hash']]
        return True

    def updatevotes(self, msg_id, vote):
        if msg_id in self.ALL_VOTES:
            self.ALL_VOTES[msg_id] += vote
        else:
            self.ALL_VOTES[msg_id] = vote
