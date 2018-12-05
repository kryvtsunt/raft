


# this class represents a server which can change states, send messages, and respond to mesages
class Server():
    def __init__(self, ID, neighbors):
        self.ID = ID
        
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
        self.state = new_state
        self.state.set_server(self)
        self.state.start()

        
