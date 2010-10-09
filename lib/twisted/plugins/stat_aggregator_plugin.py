from twisted.application.service import IServiceMaker, MultiService
from twisted.application import internet
from twisted.python import usage
from twisted.protocols import basic
from twisted.plugin import log, IPlugin
from twisted.internet import protocol

from zope.interface import implements

import simplejson as json
import time

JSONDecodeError = json.decoder.JSONDecodeError

buffers = {}

# TODO: Pull this out
class CircularBuffer:
    def __init__(self, size):
        self.buffer = [None for i in xrange(size)]

    def put(self, data):
        self.buffer.append(data)
        self.buffer.pop(0)


class DataPoint:
    def __init__(self, data):
        self.data = data
        self.timestamp = time.time()

    def __repr__(self):
        return "%s: %r" % (self.data, self.timestamp)


# TODO: Pull this out too
class AggregatorProtocol(basic.LineReceiver):
    """Protocol for receiving stats data as key-value json pairs"""

    options = {}

    def connectionMade(self):
        log.msg("There's been a connection")

    def lineReceived(self, line):
        log.msg("Received line: %s" % line)

        try:
            stats = json.loads(line)

            for stat, value in stats.items():
                if not buffers.__contains__(stat):
                    # TODO: Make this value configurable
                    buffers[stat] = CircularBuffer(10)

                buffers[stat].put(DataPoint(value)) 

        except JSONDecodeError:
            log.msg("Huh?")

        log.msg("Current buffers:")
        for name, buf in buffers.items():
            log.msg("%s: %r" % (name, buf.buffer))

    def connectionLost(self, _):
        log.msg("Connection lost")
        self.loseConnection()

class AggregatorFactory(protocol.ServerFactory):
    """Factory for our aggregation server"""

    protocol = AggregatorProtocol

    def __init__(self, options):
        self.options = options

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        p.options = self.options
        return p



# TODO: Pull this out too
class ResponderProtocol(basic.LineReceiver):
    """Protocol for returning stats data"""

    client = None

    def connectionMade(self):
        log.msg("There's been a connection")

    def lineReceived(self, line):
        log.msg("Received line: %s" % line)
        
        try:
            timestamp = float(line)
        except ValueError:
            log.msg("Bad timestamp")
            # TODO: Respond with an error

        data = {}
        
        for name, datapoints in buffers.items():
            log.msg("Name: %s Datapoints: %r" % (name, datapoints))
            data[name] = [ (dp.timestamp , dp.data) for dp in datapoints.buffer
                                                        if dp is not None and dp.timestamp > timestamp ]

        self.sendLine(json.dumps(data))

    def connectionLost(self, _):
        log.msg("Connection lost")
        self.loseConnection()

# TODO: Extract to class this and AggregatorFactory
#       When you do this, it's going to mess up logging messages
#       because of the class name - investigate contexts
class ResponderFactory(protocol.ServerFactory):
    """Factory for our response server"""

    protocol = ResponderProtocol

    def __init__(self, options):
        self.options = options

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        p.options = self.options
        return p


class Options(usage.Options):
    
    optParameters = [
        ["aggregation-port", "a", 1234, "The port number to listen on for new data"],
        ["port", "p", 4321, "The port number to listen on for returning data"],
    ]

class AggregatorMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "stat_aggregator"
    description = "A stat aggregator"
    options = Options

    def makeService(self, options):
        statsService = MultiService()

        aggServer = internet.TCPServer(int(options["aggregation-port"]), AggregatorFactory(options))
        aggServer.setServiceParent(statsService)

        responseServer = internet.TCPServer(int(options["port"]), ResponderFactory(options))
        responseServer.setServiceParent(statsService)

        return statsService

serviceMaker = AggregatorMaker()
