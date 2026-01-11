#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.protocols.ccxml import BaseCcxmlClient
from twisted.trial import unittest

class BaseCcxmlClientTestCase(unittest.TestCase):
    def setUp(self):
        self.base = BaseCcxmlClient()

    def test_send_client_event(self):
        self.base.client_event = mock.MagicMock()
        self.base.send_client_event("session", "source", "target", "event_name", "event_object")
        self.base.client_event.assert_called_once_with("session", "source", "target", "event_name", "event_object")

    def test_send_login_default(self):
        self.base.add_session = mock.MagicMock()
        self.base.send_login("session", "login", "password")
        self.base.add_session.assert_called_once_with("session", "login", "password", False)

    def test_send_login_was_connected_true(self):
        self.base.add_session = mock.MagicMock()
        self.base.send_login("session", "login", "password", True)
        self.base.add_session.assert_called_once_with("session", "login", "password", True)

    def test_send_logout(self):
        self.base.logout = mock.MagicMock()
        self.base.send_logout("session")
        self.base.logout.assert_called_once_with("session")

    def test_send_disconnected(self):
        self.base.disconnected = mock.MagicMock()
        self.base.send_disconnected("session")
        self.base.disconnected.assert_called_once_with("session")
