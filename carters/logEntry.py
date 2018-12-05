# represents a log entry with the command for the state machine and the term
# when the entry was received by leader
class LogEntry():
    def __init__(self, msg, term, index):
        self.msg = msg
        self.term = term
        self.index = index

    def get_term(self):
        return self.term

    def get_inde(self):
        return self.index

    def get_type(self):
        return self.msg['type']

    def get_src(self):
        return self.msg['src']

    def get_key(self):
        try:
            return self.msg['key']
        except KeyError:
            return None

    def get_value(self):
        try:
            return self.msg['value']
        except KeyError:
            return None

    
