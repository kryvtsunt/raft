# represents a log entry with the command for the state machine and the term
# when the entry was received by leader
class LogEntry():
    def __init__(self, msg, term, index):
        self.msg = msg
        self.term = term
        self.index = index

    def getTerm(self):
        return self.term

    def getIndex(self):
        return self.index

    def getType(self):
        return self.msg['type']

    def getSrc(self):
        return self.msg['src']

    def getKey(self):
        try:
            return self.msg['key']
        except KeyError:
            return None

    def getValue(self):
        try:
            return self.msg['value']
        except KeyError:
            return None

    
