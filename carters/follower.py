import signal
from state import State
from candidate import Candidate

class Follower(State):

    def __init__(self, timeout=2):
        super.__init__(timeout)

    
    def sig_handler(self, signum, frame):
        """If a follower times out, then they convert to a Candidate"""
        # turn off alarm
        self.signal.alarm(0)

        # tell server to switch
        self.server.switch_state(Candidate())

    def handle_append_entries(self, msg):
        super.handle_append_entries(msg)

    def handle_vote_req(self, msg):
        super.handle_append_entries(msg)

    def start(self):
        pass
