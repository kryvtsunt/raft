<<<<<<< HEAD

from logEntry import LogEntry
from state import State
from follower import Follower

=======
>>>>>>> 5037506003ff3598262b797f9a7261b4360e0a58
# this class represents a server which can change states, send messages, and respond to mesages
# consider signal.setitimer()

class Server():
    def __init__(self, ID, neighbors, sock):
        self.ID = ID
        self.sock = sock

        self.log = []
        self.neighbors = neighbors
        self.currentTerm = 0
        self.leader = None

        self.votedFor = None

        self.commitIndex = 0
        self.lastApplied = 0

        self.state = Follower()
        self.state.set_server(self)

    def swtich_state(self, new_state):
        self.state.signal.alarm(0)
        self.state = new_state
        self.state.set_server(self)
        self.state.start()

    def rec_msg(self, msg):
        self.state.rec_message(msg)

    def send_msg(self, msg):
        self.sock.sendall(json.loads(msg))

    def getLastLogTerm(self):
        try:
            last = self.log(len(self.log) - 1)
            return last.getTerm()
        except IndexError:
            return 0

    def getLastLogIndex(self):
        try:
            last = self.log(len(self.log) - 1)
            return last.getIndex()
        except IndexError:
            return 0
