#
#  store.py
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

"""Interface and implementation for stat storage."""

import rbtree


class StatStore(object):
	def saveStat(self, project, name, time, value):
		pass
		
	def getStats(self, project, name, from_time, to_time):
		pass



class MemoryStatStore(object):
	"""Stores stats in memory.

    >>> stats = MemoryStatStore()
    >>> stats.saveStat('test', 'key', 1000, 'value')
	>>> stats.saveStat('test', 'key', 2000, 'value2')
	>>> stats.saveStat('test', 'key2', 1500, 'ignored')
	>>> stats.getStats('test', 'key', 0, 5000)
	[(1000, 'value'), (2000, 'value2')]
	>>> stats.getStats('test', 'key', 500, 1500)
	[(1000, 'value')]
	"""
	
	store = {}

	
	def saveStat(self, project, name, time, value):
		self.store.setdefault(project, {})
		if name not in self.store[project]:
			self.store[project][name] = rbtree.rbtree()
		self.store[project][name][time] = value


	def getStats(self, project, name, from_time, to_time):
		if project not in self.store or name not in self.store[project]:
			return []

		result = []
		for time, value in self.store[project][name].items():
			if time < from_time:
				continue
			if time > to_time:
				break
			result.append((time, value))
		return result
