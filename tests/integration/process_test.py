#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
from cccp.process import ProcessViewer
from cccp.error import ProcessViewerError
import utils
from test_configuration import *

class test_ProcessViewer(unittest.TestCase):
	def setUp(self):
		global CCC_IP
		self.process_viewer = ProcessViewer(CCC_IP)
	def test_servers(self):
		result=self.process_viewer.servers
		self.assertTrue(len(result)>0)
	def test_server(self):
		result=None
		result=self.process_viewer.server(CCC_SERVER)
		self.assertTrue(result!=None)
		self.assertRaises(ProcessViewerError,self.process_viewer.server,DUMMY)
	def test_server_project(self):
		global CCC_SERVER
		global CCC_PROJECT_NAME
		result=None
		server=self.process_viewer.server(CCC_SERVER)
		result=server.project(CCC_PROJECT_NAME)
		self.assertTrue(result!=None)
		self.assertRaises(ProcessViewerError,server.project,DUMMY)

	def test_server_projects(self):
		global CCC_SERVER
		global CCC_PROJECT_NAME
		result=None
		result=self.process_viewer.server(CCC_SERVER).projects
		self.assertTrue(result!=None)
		self.assertTrue(len(result)>0)
		self.assertTrue(utils.find_by_name(result,CCC_PROJECT_NAME))
		utils.print_list(result,"Processus projets de "+CCC_SERVER)

	def test_project(self):
		global CCC_PROJECT_NAME
		result=None
		result=self.process_viewer.project(CCC_PROJECT_NAME)
		self.assertTrue(result!=None)
		
	def test_project_processes(self):
		global CCC_PROJECT_NAME
		result = None
		result=self.process_viewer.project(CCC_PROJECT_NAME).processes
		self.assertTrue(result!=None)
		self.assertTrue(len(result)>0)
		utils.print_list(result,"Processus du projet "+CCC_PROJECT_NAME)

	def test_process_dipatch(self):
		global CCC_SERVER
		global CCC_PROJECT_NAME
		result=self.process_viewer.server(CCC_SERVER).project(CCC_PROJECT_NAME).dispatch
		
