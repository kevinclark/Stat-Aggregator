#
#  stat.py
#  Stat-Aggregator
#
#  Copyright 2010 The Stat-Aggregator Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http:#www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS-IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from twisted.application import internet
from twisted.internet import protocol, task
from twisted.protocols import basic
from twisted.python import log

import simplejson as json


__statTracker = None


def init():
	global __statTracker
	__statTracker = StatTracker()


def incrementStat(self, name):
	global __statTracker
	__statTracker.incrementStat(name)



class StatTracker(object):
	stats = {}

	def __init__(self):
		flushLoop = task.LoopingCall(self.__flush)
		flushLoop.start(1, False)
		
		self.aggregator = StatReceiverClientFactory()
		from twisted.internet import reactor
		reactor.connectTCP('localhost', 1234, self.aggregator)


	def incrementStat(self, name):
		stats[name] = stats.get(name, 0) + 1


	def __getStatsToSend(self):
		result, self.stats = self.stats, {}
		return result


	def __flush(self):
		out = json.dumps(self.__getStatsToSend())
		if self.aggregator.instance:
			self.aggregator.instance.sendLine(out)
		print out



class StatReceiverClient(basic.LineReceiver):
	"""Protocol for a stat flush client."""

	factory = None

	def connectionMade(self):
		self.factory.instance = self

	def connectionLost(self, _):
		"""Logs the connection failure and closes the incoming connection."""
		log.err("Lost connection to the stat receiver")



class StatReceiverClientFactory(protocol.ClientFactory):
	"""Factory for a stat flush client."""
	protocol = StatReceiverClient
	instance = None
