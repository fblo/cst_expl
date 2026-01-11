#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.protocols.converter import Converter
from cccp.protocols.commons import IncrementIdReservation
from cccp.protocols.rt.subscription import Subscribable

from twisted.trial import unittest


class SubscribableTestCase(unittest.TestCase):
    def setUp(self):
        self.sub = Subscribable()

    def test_add_indicator(self):
        obj = mock.MagicMock()
        obj.name = "indic_name"

        self.sub.add_indicator(obj)

        self.assertEquals(
            self.sub.indicators['indic_name'],
            obj
        )

        self.assertRaises(
            LookupError,
            self.sub.add_indicator,
            obj
        )

    def test_del_indicator(self):
        obj = mock.MagicMock()
        obj.name = "indic_name"

        self.sub.add_indicator(obj)

        self.sub.del_indicator("indic_name")

        self.assertEquals(
            "indic_name" in self.sub.indicators,
            False
        )

        self.assertRaises(
            LookupError,
            self.sub.del_indicator,
            "indic_name"
        )

    def test_get_indicator(self):
        obj = mock.MagicMock()
        obj.name = "indic_name"

        self.sub.add_indicator(obj)

        self.assertEquals(self.sub.get_indicator("indic_name"), obj)

    def test_apply_data(self):
        data = {"indic_name": 1}

        obj = mock.MagicMock()
        obj.name = "indic_name"

        self.sub.add_indicator(obj)

        self.sub.apply_data(data)

        obj.set.assert_called_once_with(1)
