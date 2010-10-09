from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.python import usage
from twisted.protocols import basic
from twisted.plugin import log, IPlugin
from twisted.internet import protocol

from zope.interface import implements

import simplejson as json

JSONDecodeError = json.decoder.JSONDecodeError

# TODO: Pull this out
class CircularBuffer:
    def __init__(self, size):
        self.buffer = [None for i in xrange(size)]

    def put(self, data):
        self.buffer.append(data)
        self.buffer.pop(0)

class Options(usage.Options):
    
    optParameters = [
        ["port", "p", 1234, "The port number to listen on"],
    ]


class AggregatorProtocol(basic.LineReceiver):
    """Protocol for receiving stats data"""

    options = {}
    buffers = {}

    def connectionMade(self):
        log.msg("There's been a connection")

    def lineReceived(self, line):
        log.msg("Received line: %s" % line)

        try:
            stats = json.loads(line)

            for stat, value in stats.items():
                if not self.buffers.__contains__(stat):
                    # TODO: Make this value configurable
                    self.buffers[stat] = CircularBuffer(10)

                self.buffers[stat].put(value) 

        except JSONDecodeError:
            log.msg("Huh?")

        log.msg("Current buffers:")
        for name, buf in self.buffers.items():
            log.msg("%s: %r" % (name, buf.buffer))

        # now we parse the data

    def connectionLost(self, _):
        log.msg("Connection lost")
        self.factory.server.transport.loseConnection()

class AggregatorFactory(protocol.ServerFactory):
    """Factory for our aggregation server"""

    protocol = AggregatorProtocol

    def __init__(self, options):
        self.options = options

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        p.options = self.options
        return p

class AggregatorMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "stat_aggregator"
    description = "A stat aggregator"
    options = Options

    def makeService(self, options):
        return internet.TCPServer(int(options["port"]), AggregatorFactory(options))

serviceMaker = AggregatorMaker()
