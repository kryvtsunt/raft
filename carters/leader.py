import signal
from state import State

APPEND = "appendEntries"
APPEND_RSP = "appendEntriesResponse"
VOTE_REQ = "voteRequest"
VOTE_REQ_RSP = "voteRequestResponse"

class Leader(State):

    def __init__(self, timeout=1):
        super.__init__(timeout)


    def sig_handler(self, signum, frame):
        # turn alarm ON
        self.signal.alarm(0)

        # send out heartbeat
        self.send_heartbeats()

        # turn alarm ON
        self.signal.alarm(self.timeout)

    
"""
msg = {
    src          : neighbor
    dst          : my_id
    leader       : FFFF      ?
    type         : req_vote
    MID          : ...
    term         : candidate's term
    candidateID  : neighbor
    lastLogIndex : last log entry index
    lastLogTerm  : last log entry term
"""
    def handle_vote_req(self, msg):
        #super.handle_vote_req(msg)
        pass

    def handle_append_entries_rsp(self, msg):
        #super.handle_append_entries_rsp(msg)
        pass

    def start(self):
        self.send_heartbeats()

    def send_heartbeats(self):
        for n in self.server.neighbors:
            msg = {'src':self.server.ID,
                   'dst':n,
                   'leader':None,
                   'type':VOTE_REQ,
                   'MID':None, # TODO, fix?
                   'term':self.server.currentTerm,
                   'candidateID':self.server.ID,
                   'lastLogIndex':self.server.getLastLogIndex(),
                   'lastLogTerm':self.server.getLastLogTerm()}
            self.server.send_msg(msg)

        return None
            
