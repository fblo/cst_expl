#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>
#	- SLAU <slau@interact-iv.com>

import unittest
from integration.conf_ccxml_test import test_CcxmlConf

suite = unittest.TestLoader().loadTestsFromTestCase(test_CcxmlConf)
unittest.TextTestRunner(verbosity=2).run(suite)
