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
        # ALL_VOTES will be an aggregate of all the votes on the messages and will be a dict as follows:
        '''
            {
                "msg_id": vote_count
            }
        '''

        self.BLOCKS = []
        # self.AWAITING = []
        self.ALL_VOTES = {}

    def logvote(self, link_ring_sig, msg_id, vote):
        '''
            processing a vote
        '''
        new_block = {
            "link_ring_sig": link_ring_sig,
            "msg_id": msg_id,
            "points": vote
        }
        salt = self.signblock(new_block)
        new_block['salt'] = salt
        self.BLOCKS.append(new_block)

    def signblock(self, new_block):
        '''
            should be called by the server so that the results can be broadcasted
            We can make this signing as easy as possible
        '''
        prev_hash = self.BLOCKS[-1]
        salt = None

        return salt

    def verifysignature(self, new_block, salt):
        '''
            We can make this crypto as easy or as difficult as we want
        '''
        print("Automatic signature approval")
        return True

    def 
