#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
from cccp.requester import HeadRequester, DispatchRequester
from test_configuration import *

class test_HeadRequester(unittest.TestCase):
	def setUp(self):
		global CCC_IP
		global CCC_PROJECT_NAME
		self.requester = HeadRequester(CCC_IP)
	def test_search_paths(self):
		self.assertTrue(len(self.requester.search_paths("/db/projects/Main/processes","Head_Main"))>0)

class test_DispatchRequester(unittest.TestCase):
	def setUp(self):
		global CCC_SERVER_NAME
		global CCC_IP
		global CCC_PROJECT_NAME
		self.requester = DispatchRequester(CCC_SERVER_NAME,CCC_PROJECT_NAME,CCC_IP)
	def test_list(self):
		global CCC_PROJECT_NAME
		result = None
		result = self.requester.get_list("sessions")
		print result	


