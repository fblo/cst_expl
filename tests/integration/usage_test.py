#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
from time import sleep
from cccp.db import UsageDB
from cute import CallBot
from test_configuration import *

class test_Usage(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.usage_db = UsageDB(CCC_PROJECT_NAME,CCC_SERVER_NAME,CCC_IP)
		self.callbot = CallBot(CALLBOT_SIP_PORT)
	def test_simple_request(self):
		request={ "sessions" : { "session_id" : ""} }
		result=self.usage_db.query(request)
		nb_sessions = len(result["sessions"])
		self.callbot.Call(CCC_PROJECT_SIP_URI)
		print "Wait 1s"
		sleep(1)
		result=self.usage_db.query(request)
		self.assertTrue(len(result["sessions"]) == nb_sessions+1)
	def test_multi_criteria(self):
		request={"sessions" : { "session_id" : "","project_name" : "TestAuto", "session_type" :1}}	
		result=self.usage_db.query(request)
	@classmethod
	def tearDownClass(self):
		self.callbot.ShutDown()	
		del self.callbot 
