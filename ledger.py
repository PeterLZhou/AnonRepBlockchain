import util

class Ledger:
    def __init__(self):
        # each block is a dictionary as follows:
        '''
            {
                "link_ring_sig": linkable-ring-signature of the client making the upvote
                "msg_id": message id of the message that is being voted on
                "points": the amount of reputation points that is being sent
                "salt": the salt that verifies the block has not be tampered with
                            salt is none if the block is in the awaiting list
            }
        '''

        self.BLOCKS = {}
        self.TAIL_BLOCK = -1 # default starting block
        self.ALL_VOTES = {}
        # ALL_VOTES will be an aggregate of all the votes on the messages and will be a dict as follows:
        '''
            {
                "msg_id": vote_count
            }
        '''
    def appendblock(self, new_block):
        self.BLOCKS.insert(new_block)
        self.TAIL_BLOCK = util.sha256hash(str(new_block))

    def logvote(self, link_ring_sig, msg_id, vote):
        '''processing a vote, should only be called by lead server
        '''
        new_block = {
            "link_ring_sig": link_ring_sig,
            "msg_id": msg_id,
            "points": vote
            "prev_block": self.TAIL_BLOCK
        }
        self.updatevotes(msg_id, vote)
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
            if verifysignature(self.TAIL_BLOCK, salt):
                break
            count += 1

        return salt

    def verifysignature(self, prev_hash, salt):
        '''
            We can make this crypto as easy or as difficult as we want
        '''
        result = util.sha256hash(prev_hash + salt)
        if ord(result[0]) < 10:
            return True
        else:
            return False

    def updatevotes(self, msg_id, vote):
        if msg_id in self.ALL_VOTES:
            self.ALL_VOTES[msg_id] += vote
        else:
            self.ALL_VOTES[msg_id] = vote
