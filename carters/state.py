import signal

APPEND = "appendEntries"
APPEND_RSP = "appendEntriesResponse"
VOTE_REQ = "voteRequest"
VOTE_REQ_RSP = "voteRequestResponse"



# this class is an abstract state. it will represent a follower, candidate, or leader
class State():

    # timeout must be an int seconds
    def __init__(self, timeout):
        self.timeout = timeout
        self.signal = signal.signal(signal.SIGALRM, self.sig_handler)
        self.signal.alarm(timeout)
    
    def set_server(self, server):
        self.server = server

    def rec_message(self, msg):
        self.resetAlarm()
        
        # For now, fail get() and put() from clients
        if msg['type'] in ['get', 'put']:
            rsp = {'src':my_id,
                   'dst':msg['src'],
                   'leader':None,
                   'type':'fail',
                   'MID':msg['MID']}

        if msg['type'] == APPEND:
            self.handle_append_entries(msg)
        elif msg['type'] == APPEND_RSP:
            self.handle_append_entries_rsp(msg)
        elif msg['type'] == VOTE_REQ:
            self.handle_vote_req(msg)
        elif msg['type'] == VOTE_REQ_RSP:
            self.handle_vote_req_rsp(msg)
        else:
            raise RuntimeError("Unexpected message")

    # for everyone
    def sig_handler(self, signum, frame):
        raise RuntimeError("TODO")
    
    # for followers and candidates
    def handle_append_entries(self, msg):
        raise RuntimeError("TODO")

    # for leaders
    def handle_append_entries_rsp(self, msg):
        raise RuntimeError("TODO")

    # for everyone
    def handle_vote_req(self, msg):
        raise RuntimeError("TODO")

    # for candidates
    def handle_vote_req_rsp(self, msg):
        raise RuntimeError("TODO")

    # for everyone
    def start(self):
        raise RuntimeError("TODO")

    def candidateLogUpToDate(self, lastLogIndex, lastLogTerm):
        if self.server.getLastLogTerm() < lastLogTerm:
            return True
        elif (self.server.getLastLogTerm() == lastLogTerm) and\
             (self.server.getLastLogIndex() < lastLogIndex):
            return True
        else:
            return False

    def resetAlarm(self):
        # turn alarm OFF
        self.signal.alarm(0)

        # turn alarm ON
        self.signal.alarm(self.timeout)





    
