#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
import cccp.land.idx as il

# To use indexed_object :
#     - call the indexed_object constructor by specifying the getter and setter of the indexed property

#     - call the set_dict_idx(old_value) at the end of the setter of the indexed property
# See howto.txt for more details.
class olo(il.indexed_object):
	def __init__(self):
		il.indexed_object.__init__(self, self.get_glups, self.set_glups)
		self._glups='plonk'
	def get_glups(self):
		return self._glups
	def set_glups(self,value):
		old_value=self._glups
		self._glups=value
		self.set_dict_idx(old_value)
	glups = property(get_glups,set_glups)

class test_indexed_objects_dict(unittest.TestCase):
	def test_idx_object(self):
		# Create my olo indexed_object
		o = olo()
		# Create an indexed object dictionary
		oo = il.indexed_objects_dict()
		# Add an indexed object to the indexed dictionary
		oo.add(o)
		# Assert that all the indexes are the same
		self.assertEqual(o.glups, 'plonk')
		self.assertEqual(o.idx, 'plonk')
		for x in oo:
			self.assertEqual(x, 'plonk')

		o.glups = 'chplouc'

		# Assert that all the indexes are the same
		self.assertEqual(o.glups, 'chplouc')
		self.assertEqual(o.idx, 'chplouc')
		for x in oo:
			self.assertEqual(x, 'chplouc')

		o.idx = 'koko'

		# Assert that all the indexes are the same
		self.assertEqual(o.glups, 'koko')
		self.assertEqual(o.idx, 'koko')
		for x in oo:
			self.assertEqual(x, 'koko')
			
