import signal
from state import State

APPEND = "appendEntries"
APPEND_RSP = "appendEntriesResponse"
VOTE_REQ = "voteRequest"
VOTE_REQ_RSP = "voteRequestResponse"


class Candidate(State):
    def __init__(self, timeout=3):
        super.__init__(timeout)
        self.num_votes = 0

    # TODO can allow candidates to send out vote_reqs twice before timing out
    def sig_handler(self, signum, frame):
        # turn off alarm
        self.signal.alarm(0)

        # start another election
        self.election()

        # reset alarm
        self.signal.alarm(self.timeout)

    def handle_append_entries(self, msg):
        # super.handle_append_entries(msg)

        # switch to follower for now
        self.server.switch_state(Follower())

        # update everything for now
        self.server.leader = msg['leader']
        self.server.currentTerm = msg['term']
        # reply true for now
        rsp = {'src': self.server.ID,
               'dst': msg['src'],
               'leader': self.server.leader,
               'type': APPEND_RSP,
               'MID': msg['MID'],
               'term': self.server.currentTerm,
               'success': True}
        self.server.send_msg(rsp)
        return None

    def handle_vote_req(self, msg):
        # super.handle_append_entries(msg)

        # rules for all servers (2)
        if msg['term'] > self.server.currentTerm:
            self.server.currentTerm = msg['term']
            self.server.votedFor = None
            self.server.switch_state(Follower())

        # receiver implementation (1)
        if msg['term'] < self.server.currentTerm:
            rsp = {'src': self.server.my_id,
                   'dst': msg['src'],
                   'leader': self.server.leader,
                   'type': VOTE_REQ_RSP,
                   'MID': msg['MID'],
                   'term': self.server.currentTerm,
                   'voteGranted': False}
            self.server.send_msg(rsp)
            return None

        # receiver implementation (2)
        if (self.votedFor == None or self.votedFor == msg['candidateID']) and \
                (self.candidateLogUpToDate(msg['lastLogIndex'], msg['lastLogTerm'])):
            rsp = {'src': self.server.my_id,
                   'dst': msg['src'],
                   'leader': self.server.leader,
                   'type': VOTE_REQ_RSP,
                   'MID': msg['MID'],
                   'term': self.server.currentTerm,
                   'voteGranted': False}
            self.server.send_msg(rsp)
            self.votedFor = msg['candidateID']
            return None

        # if all else fails, reply false ?
        rsp = {'src': self.server.my_id,
               'dst': msg['src'],
               'leader': self.server.leader,
               'type': VOTE_REQ_RSP,
               'MID': msg['MID'],
               'term': self.server.currentTerm,
               'voteGranted': False}
        self.server.send_msg(rsp)
        return None

    def handle_vote_req_rsp(self, msg):
        # super.handle_vote_req_rsp(msg)

        # rules for all servers (2)
        if msg['term'] > self.server.currentTerm:
            self.server.currentTerm = msg['term']
            self.server.votedFor = None
            self.server.switch_state(Follower())

        # ignore anything before this current term ?
        if msg['term'] < self.server.currentTerm:
            # ignore
            return None

        self.num_votes += 1

        if self.num_votes > len(self.server.neighbors) / 2:
            self.server.switch_state(Leader())
            return None

        return None

    def start(self):
        self.election()




    def election(self):
        self.server.currentTerm += 1
        self.leader = None
        self.server.votedFor = self.server.ID
        self.num_votes = 1  # need to reset votes from term to term

        for n in self.server.neighbors:
            msg = {'src': self.server.ID,
                   'dst': n,
                   'leader': None,
                   'type': VOTE_REQ,
                   'term': self.server.currentTerm,
                   'candidateID': self.server.ID,
                   'lastLogIndex': self.server.getLastLogIndex(),
                   'lastLogTerm': self.server.getLastLogTerm()}
            self.server.send_msg(msg)
        return None
