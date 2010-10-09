
class CircularBuffer:
    def __init__(self, size):
        self.buffer = [None for i in xrange(size)]

    def put(self, data):
        self.buffer.append(data)
        self.buffer.pop(0)


