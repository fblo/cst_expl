#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
from cccp.db import ConfigDB
from test_configuration import *

class test_Deserializer(unittest.TestCase):
	def setUp(self):
                global CCC_IP
                self.db = ConfigDB(CCC_IP)
	def test_ccxml_process(self):
		o=None
		o = self.db.get(CCC_PROJECT_PROCESSES_PATH+"/Ccxml_"+CCC_PROJECT_NAME)
		self.assertTrue(o is not None)
	def test_voip_process(self):
		o=None
		o = self.db.get(CCC_PROJECT_PROCESSES_PATH+"/Voip_"+CCC_PROJECT_NAME)
		self.assertTrue(o is not None)
