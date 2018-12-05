import signal
from state import State

class Candidate(State):

    def __init__(self, timeout=3):
        super.__init__(timeout)

    # TODO can allow candidates to send out vote_reqs twice before timing out
    def sig_handler(self, signum, frame):
        # turn off alarm
        self.signal.alarm(0)

        # start another election
        self.election()

        # reset alarm
        self.signal.alarm(self.timeout)

        

    def handle_append_entries(self, msg):
        super.handle_append_entries(msg)

    def handle_vote_req(self, msg):
        super.handle_append_entries(msg)
        
    def handle_vote_req_rsp(self, msg):
        super.handle_vote_req_rsp(msg)

    def start(self):
        self.election()

    def election(self):
        self.server.currentTerm += 1
        self.server.votedFor = self.server.ID

        for n in self.server.neighbors:
            # send out vote rec for n
