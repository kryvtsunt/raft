APPEND = "appendEntries"
APPEND_RSP = "appendEntriesResponse"
VOTE_REQ = "voteRequest"
VOTE_REQ_RSP = "voteRequestResponse"

# messages, one of the four above
class Message():

    def __init__(self, msg_type, src, dest, term, data):
        self.type = msg_type
        self.src = src
        self.dest = dest
        self.term = term
        self.data = data
