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
from cccp.error import ConfigDBError
from test_configuration import *

class test_ConfigDB(unittest.TestCase):
	def setUp(self):
		global CCC_IP
		self.config_db = ConfigDB(CCC_IP)
	def test_bad_path_in_ls(self):
		self.assertRaises(ConfigDBError,self.config_db.list,"/db/xXx")
	def test_empty_node_in_ls(self):
		result = self.config_db.list("/db/projects/"+CCC_PROJECT_NAME+"/Voip.xml")
		self.assertTrue(len(result) == 0)
	def test_builtin_mode_in_get(self):
		d={}
		self.assertRaises(ConfigDBError,self.config_db.put,"/db/poubelle/builtin",d)
