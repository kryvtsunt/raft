#!/usr/bin/env python

import sys, socket, select, time, json, random

DEBUG = False
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

VOTE_REQUEST = "vote_request"
VOTE_REJECT = "vote_reject"
VOTE_APPROVE = "vote_approve"
APPEND_REQUEST = "append_request"
APPEND_APPROVE = "append_approve"
HEARTBEAT = "heartbeat"

HEARTBEAT_RESPONSE = "heartbeat_response"


class Raft:
    def __init__(self):
        # ids
        self.my_id = sys.argv[1]
        self.replica_ids = sys.argv[2:]

        self.state = FOLLOWER
        self.leader = 'FFFF'
        self.term = 0

        self.q = []
        self.log = []
        self.store = {}

        self.votes = 0
        self.voted_for = 'FFFF'
        self.last = None
        self.election_time = None
        self.leader_timeout = 0.5
        self.election_timeout = random.uniform(0.1, 0.3)

        self.commit_index = 0
        self.last_applied = 0

        # LEADER ONLY
        self.next_index = []
        self.match_index = []

        # Connect to the network. All messages to/from other replicas and clients will
        # occur over this socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.sock.connect(self.my_id)

    def run(self):
        # MOVE OUTSIDE
        if self.last is None:
            self.last = time.time()
        if self.election_time is None:
            self.election_time = time.time()

        while True:

            # ------------------------------------ ELECTION
            if self.state == FOLLOWER:
                self.frun()

            elif self.state == CANDIDATE:
                self.crun()

            elif self.state == LEADER:
                self.lrun()


            ready = select.select([self.sock], [], [], 0.1)[0]
            if self.sock in ready:
                msg_raw = self.sock.recv(32768)

                if len(msg_raw) == 0:
                    continue

                msg = json.loads(msg_raw)
                self.print_info(msg)

                if msg['type'] == HEARTBEAT:
                    self.respond_heartbeat(msg)

                if msg['src'] == self.leader:
                    self.last = time.time()


                # ---------------------------------------MESSAGE HANDLER
                if msg['type'] in ['get', 'put']:
                    self.respond_client_request(msg)

                elif msg['type'] == APPEND_REQUEST:
                    self.respond_append_request(msg)

                elif msg['type'] == VOTE_REQUEST:
                    self.respond_vote_request(msg)

                elif msg['type'] == VOTE_APPROVE and self.state == CANDIDATE:
                    self.respond_election(msg)





    def frun(self):
        clock = time.time()
        if clock - self.last > self.leader_timeout or self.leader == 'FFFF':
            clock = time.time()
            if clock - self.election_time > self.election_timeout:
                # if self.voted_for is None:
                self.state = CANDIDATE
                self.start_election()

    def crun(self):
        clock = time.time()
        if clock - self.election_time > self.election_timeout:
            self.start_election()

    def lrun(self):
        self.send_heartbeat()

    def respond_client_request(self, msg):
        if self.state == LEADER:
            self.respond_client(msg)
            for replica in self.replica_ids:
                log_msg = {"src": self.my_id, "dst": replica, "leader": self.leader, "type": APPEND_REQUEST,
                           'content': self.get_log()}
                self.sock.send(json.dumps(log_msg))
        elif self.leader != 'FFFF':
            # redirect to leader
            redirect = {"src": msg['dst'], "dst": msg['src'], "leader": self.leader, "type": "redirect",
                        "MID": msg['MID']}
            self.sock.send(json.dumps(redirect))
        else:
            # print(msg['MID'])
            # redirect = {"src": msg['dst'], "dst": msg['src'], "leader": self.my_id, "type": "redirect",
            #             "MID": msg['MID']}
            # self.sock.send(json.dumps(redirect))
            self.q.append(msg)

    def respond_append_request(self, msg):
        self.update_log(msg)
        # respond_msg = {"src": self.my_id, "dst": self.leader, "leader": self.leader, "type": APPEND_APPROVE}
        # self.sock.send(json.dumps(respond_msg))

    def update_log(self, msg):
        for m in msg['content']:
            if m not in self.log:
                self.add_log(m)
                self.store[m['key']] = m['value']

    def respond_election(self, msg):
        self.votes += 1
        if self.votes >= 3:
            self.state = LEADER
            self.leader = self.my_id
            if DEBUG:
                print('I am the new leader ' + str(self.leader))
            self.votes = 0
            self.next_index = [len(self.log) + 1 for n in self.replica_ids]
            self.match_index = [0 for n in self.replica_ids]
            self.store = {}
            self.create_store()

    def start_election(self):
        self.term += 1
        self.leader = 'FFFF'
        self.votes=1
        self.voted_for = self.my_id
        self.election_time = time.time()
        if DEBUG:
            print('[%f] %s has started an election' % (time.time(), self.my_id))
        self.request_vote()

    def request_vote(self):
        for replica in self.replica_ids:
            vote = {'src': self.my_id, 'dst': replica, 'leader': self.leader,
                    'type': VOTE_REQUEST, 'term': self.term}
            self.sock.send(json.dumps(vote))

    def respond_vote_request(self, msg):
        self.election_time = time.time()
        self.leader = 'FFFF'

        ###### Carter's code

        # # rules for all servers (2)
        # if msg['term'] > self.term:
        #     self.term = msg['term']
        #     self.leader = 'FFFF'
        #     self.voted_for = 'FFFF'
        #     self.state = FOLLOWER
        #
        # # receiver implementation (1)
        # if msg['term'] < self.term:
        #     rsp = {'src': self.my_id, 'dst': msg['src'], 'leader': self.leader, 'type': VOTE_REJECT,
        #            'term': self.term}
        #     self.sock.send(json.dumps(rsp))
        # # receiver implementation (2)
        # elif (self.voted_for == 'FFFF' or self.voted_for == msg['src']) and (
        #         self.candidateLogUpToDate(msg['last_index'], msg['last_term'])):
        #     self.voted_for = msg['src']
        #     self.leader = msg['src']
        #     rsp = {'src': self.my_id, 'dst': msg['src'], 'leader': self.leader, 'type': VOTE_APPROVE,
        #                'term': self.term}
        #
        #     self.sock.send(json.dumps(rsp))
        # else:
        #     rsp = {'src': self.my_id, 'dst': msg['src'], 'leader': self.leader, 'type': VOTE_REJECT,
        #            'term': self.term}
        #     self.sock.send(json.dumps(rsp))
        ######



        if self.term >= msg['term']:
            response = {'src': self.my_id, 'dst': msg['src'], 'leader': self.leader,
                        'type': VOTE_REJECT}
        else:
            # TODO log stuff | check if vote for is none or same replica
            self.term = msg['term']
            self.leader = msg['src']
            self.voted_for = msg['src']
            self.state = FOLLOWER
            response = {'src': self.my_id, 'dst': msg['src'], 'leader': self.leader,
                        'type': VOTE_APPROVE, 'term': self.term}
        self.sock.send(json.dumps(response))

    def respond_client(self, msg):
        if msg['type'] == 'put':
            self.add_log(msg)
            self.store[msg['key']] = msg['value']
            resp = {'src': self.my_id, 'dst': msg['src'],
                    'leader': self.my_id, 'MID': msg['MID'], 'type': 'ok'}
            self.sock.send(json.dumps(resp))
        elif msg['type'] == 'get':
            if msg['key'] in self.store:
                value = self.store[msg['key']]
                resp = {'src': self.my_id, 'dst': msg['src'],
                        'leader': self.my_id, 'MID': msg['MID'], 'type': 'ok', 'value': value}
                self.sock.send(json.dumps(resp))
            else:
                resp = {'src': self.my_id, 'dst': msg['src'],
                        'leader': self.my_id, 'MID': msg['MID'], 'type': 'fail'}
                self.sock.send(json.dumps(resp))

    def get_log(self):
        log = []
        for i in range(50,0,-1):
            if (len(self.log)<i):
                continue
            log.append(self.log[len(self.log)-i])
        # print(log)
        return log

    def send_heartbeat(self):
        clock = time.time()
        if clock - self.last > .25:
            for replica in self.replica_ids:
                msg = {'src': self.my_id, 'dst': replica, 'leader': self.leader, 'term': self.term, 'type': HEARTBEAT}
                self.sock.send(json.dumps(msg))
            self.last = clock

    def respond_heartbeat(self, msg):
        if msg['term'] >= self.term:
            self.state = FOLLOWER
            self.last = time.time()
            self.leader = msg['src']
            self.voted_for = 'FFFF'
            self.votes = 0
            log_msg = {"src": self.my_id, "dst": self.leader, "leader": self.leader, "type": APPEND_REQUEST,
                       'content': self.get_log()}
            self.sock.send(json.dumps(log_msg))

        for msg in self.q:
            redirect = {"src": msg['dst'], "dst": msg['src'], "leader": self.leader, "type": "redirect",
                        "MID": msg['MID']}
            self.sock.send(json.dumps(redirect))
        self.q = []

    def create_store(self):
        for msg in self.log:
            self.store[msg['key']] = msg['value']

    # UTIL FUNCTIONS

    def print_info(self, msg):
        pass
        if DEBUG:
            # print('[%f] %s received a %s from %s' % (time.time(), msg['dst'], msg['type'], msg['src']))
            print('%s believes %s is the leader, and he is %s' % (self.my_id, self.leader, self.state))
            # print(str(self.store))

    def add_log(self, msg):
        # log_msg = {"term": self.term, "content": msg}
        message = {'key': msg['key'], 'value': msg['value']}
        self.log.append(message)

    def candidateLogUpToDate(self, lastLogIndex, lastLogTerm):
        if self.getLastLogTerm() < lastLogTerm:
            return True
        elif self.getLastLogTerm() == lastLogTerm and self.getLastLogIndex() <= lastLogIndex:
            return True
        else:
            return False

    def getLastLogTerm(self):
        try:
            last = self.log[len(self.log) - 1]['term']
            return last
        except IndexError:
            return 0

    def getLastLogIndex(self):
        return len(self.log)


if __name__ == "__main__":
    server = Raft()
    server.run()