#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from cccp.protocols.converter import Converter

from twisted.trial import unittest

class ConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.con = Converter()

    def test_init(self):
        pass

    def test_next_field_index(self):
        self.con._field_index = 0
        result = self.con._next_field_index()
        self.assertEquals(result, 1)
