#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

from cccp.db import ConfigDB
from unittest import TestCase
from test_configuration import *

class test_Protocol(TestCase):
	def setUp(self):
                global CCC_IP
                self.db = ConfigDB(CCC_IP)
	def test_print_object(self):
		o=None
		o = self.db.get(CCC_PROJECT_PROCESSES_PATH+"/Voip_"+CCC_PROJECT_NAME)
		print o
