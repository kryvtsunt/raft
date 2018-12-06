import signal
from state import State
from candidate import Candidate

APPEND = "appendEntries"
APPEND_RSP = "appendEntriesResponse"
VOTE_REQ = "voteRequest"
VOTE_REQ_RSP = "voteRequestResponse"

class Follower(State):

    def __init__(self, timeout=2):
        super.__init__(timeout)

    
    def sig_handler(self, signum, frame):
        """If a follower times out, then they convert to a Candidate"""
        # turn off alarm
        self.signal.alarm(0)

        # tell server to switch
        self.server.switch_state(Candidate())

"""
rsp = {
    src     : my_id
    dst     : msg['src']
    leader  : leader
    type    : vote_req_rsp
    MID     : msg['MID']
    term    : currentTerm
    success : True/False
"""
    def handle_append_entries(self, msg):
        #super.handle_append_entries(msg)

        # update everything for now
        self.server.leader = msg['leader']
        self.server.currentTerm = msg['term']
        # reply true for now
        rsp = {'src':self.server.ID,
               'dst':msg['src'],
               'leader':self.server.leader,
               'type':APPEND_RSP,
               'MID':msg['MID'],
               'term':self.server.currentTerm,
               'success':True}
        self.server.send_msg(rsp)
        return None
        

"""
msg = {
    src          : neighbor
    dst          : my_id
    leader       : None
    type         : req_vote
    MID          : ...
    term         : candidate's term
    candidateID  : neighbor
    lastLogIndex : last log entry index
    lastLogTerm  : last log entry term
"""
"""
rsp = {
    src         : my_id
    dst         : msg['src']
    leader      : leader
    type        : vote_req_rsp
    MID         : msg['MID']
    term        : currentTerm
    voteGranted : True/False
"""
    def handle_vote_req(self, msg):
        #super.handle_append_entries(msg)

        # rules for all servers (2)
        if msg['term'] > self.server.currentTerm:
            self.server.currentTerm = msg['term']
            self.server.votedFor = None
            self.server.switch_state(Follower())

        # receiver implementation (1)
        if msg['term'] < self.server.currentTerm:
            rsp = { 'src':self.server.my_id,
                    'dst':msg['src'],
                    'leader':self.server.leader,
                    'type':VOTE_REQ_RSP,
                    'MID':msg['MID'],
                    'term':self.server.currentTerm,
                    'voteGranted':False}
            self.server.send_msg(rsp)
            return None

        # receiver implementation (2)
        if (self.votedFor == None or self.votedFor == msg['candidateID']) and\
       (self.candidateLogUpToDate(msg['lastLogIndex'], msg['lastLogTerm'])):
            rsp = { 'src':self.server.my_id,
                    'dst':msg['src'],
                    'leader':self.server.leader,
                    'type':VOTE_REQ_RSP,
                    'MID':msg['MID'],
                    'term':self.server.currentTerm,
                    'voteGranted':False}
            self.server.send_msg(rsp)
            self.votedFor = msg['candidateID']
            return None

        raise RuntimeError("Unexpected behavior! follower.py, handle_vote_req()")



    def start(self):
        pass
