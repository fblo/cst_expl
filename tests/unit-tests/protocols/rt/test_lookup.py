#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from cccp.protocols.rt.indicators import (
    UsersCount,
    UserTotalTasksCount,
)
from cccp.protocols.rt.lookup import IndicatorLuT


from twisted.trial import unittest


class IndicatorLuTTestCase(unittest.TestCase):
    def setUp(self):
        self.lut = IndicatorLuT()

    def test_get_indicators_session(self):
        result = self.lut.get_indicators(
            "username",
            "session",
            "profile",
            ["user_total_tasks_count"]
        )
        self.assertIsInstance(result[0], UserTotalTasksCount)

    def test_get_indicators_service(self):
        result = self.lut.get_indicators(
            "username",
            "service",
            None,
            ["users_count"]
        )
        self.assertIsInstance(result[0], UsersCount)

    def test_get_indicators_session_failure_no_profile(self):
        self.assertRaises(
            LookupError,
            self.lut.get_indicators,
            "username",
            "session",
            None,
            ["user_total_tasks_count"]
        )

    def test_get_indicators_session_failure_unknown_indicator(self):
        self.assertRaises(
            LookupError,
            self.lut.get_indicators,
            "username",
            "session",
            "profile",
            ["invalid_indic"]
        )

    def test_get_indicators_service_failure_unknown_indicator(self):
        self.assertRaises(
            LookupError,
            self.lut.get_indicators,
            "username",
            "service",
            None,
            ["invalid_indic"]
        )

    def test_get_indicators_failure_invalid_type(self):
        self.assertRaises(
            LookupError,
            self.lut.get_indicators,
            "username",
            "invalid_type",
            None,
            ["invalid_indic"]
        )
