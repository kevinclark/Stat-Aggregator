#
#  statdemo_plugin.py
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

from stataggregator import stats

from twisted.application import internet, service
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web import resource, server

from zope.interface import implements


class Options(usage.Options):
	"""Options for this plugin."""

	optParameters = [
		["port", "p", 1212, "The port number to listen on."],
	]


class StatDemoResource(resource.Resource):
	def __init__(self):
		resource.Resource.__init__(self)
		self.putChild('', self)

  	def render(self, request):
		"""Renders the resource."""
		stats.incrementStat('requests')
		return "OK"


class StatDemoMaker(object):
	implements(service.IServiceMaker, IPlugin)

	tapname = "statdemo"
	description = "Demonstrates stat collection."
	options = Options

	def makeService(self, options):
		"""Construct a service."""
		stats.init()
		return internet.TCPServer(options['port'], server.Site(StatDemoResource()))


serviceMaker = StatDemoMaker()