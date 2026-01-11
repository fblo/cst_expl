#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- SLAU <slau@interact-iv.com>

CALLBOT_SIP_PORT = 32123

CCC_IP = '10.199.30.25'
CCC_PROJECT_NAME = 'TestAuto'
CCC_PROJECT_SIP_PORT = 21002
CCC_PROJECT_SIP_URI = 'sip:auto@%s:%s' % (CCC_IP, CCC_PROJECT_SIP_PORT)
CCC_SERVER_NAME = 'consistent'
CCC_PROJECT_PROCESSES_PATH = '/db/projects/%s/processes/%s/Head_Main/Head_%s' % (CCC_PROJECT_NAME, CCC_SERVER_NAME, CCC_PROJECT_NAME)

CDB_PROJECTS_PATH = '/db/projects'

CONF_DEFAULT_AGENT_PROFILE_NAME = 'profil_agent'
CONF_DEFAULT_GROUP_NAME = 'default_group'
CONF_CCXML_NAME = 'Ccxml_%s.xml' % CCC_PROJECT_NAME

DUMMY = 'xXx'
