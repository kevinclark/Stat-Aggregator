import time

class DataPoint:
    def __init__(self, data):
        self.data = data
        self.timestamp = time.time()

    def __repr__(self):
        return "%s: %r" % (self.timestamp, self.data)

