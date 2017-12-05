class Ledger:
    def __init__(self):
        # each block is a dictionary as follows:
        '''
            {
                "link_ring_sig": linkable-ring-signature of the client making the upvote
                "msg_id": message id of the message that is being voted on
                "points": the amount of reputation points that is being sent
                "signature": the signature that verifies the block has not be tampered with
                            signature is none if the block is in the awaiting list
            }
        '''
        # ALL_VOTES will be an aggregate of all the votes on the messages and will be a dict as follows:
        '''
            {
                "msg_id": vote_count
            }
        '''

        self.BLOCKS = []
        self.AWAITING = []
        self.ALL_VOTES = {}

    def log_vote(self, link_ring_sig, msg_id, vote):
        '''
            processing a vote
        '''
        new_block = {
            "link_ring_sig": link_ring_sig,
            "msg_id": msg_id,
            "points": vote,
            "signature": None
        }
        self.awaiting.append(new_block)
        # return self.propose_block(new_block)

    # def propose_block(self, new_block):
    #     # verify that the transaction of the block is legal by looking at the history of the chain
    #     # returns True if the transaction is legal, False otherwise
    #     sender_value = 0
    #     for block in self.blocks:
    #         if block["Sender"] == new_block["Sender"]:
    #             sender_value -= block["Points"]
    #         if block["Receiver"] == new_block["Sender"]:
    #             sender_value += block["Points"]

    #     if sender_value >= new_block["Points"]:
    #         self.awaiting.append(new_block)
    #         return True
    #     else:
    #         return False
        # ledger needs to be broadcasted

    def sign_block(self, new_block):
        '''
            should be called by the server so that the results can be broadcasted
            We can make this signing as easy as possible
        '''
        signature = None
        return signature

    def process_ledger(self, new_ledger):
        ''' decide if new ledger is more up to date than current ledger
        '''
        # decide whether or not new_ledger is more up-to-date, i.e. it's longer
        # verify that all the new ledger is secure based on the sigatures
        self.blocks = new_ledger.blocks
        self.awaiting = new_ledger.awaiting
        pass

    def _verify_signature(self, new_block, signature):
        '''
            We can make this crypto as easy or as difficult as we want
        '''
        print("Automatic signature approval")
        return True

    def _append_block(self, new_block, signature):
        # verify legality of block
        if self.verify_signature(new_block, signature):
            self.blocks.append(new_block)
        # ledger needs to be broadcasted
