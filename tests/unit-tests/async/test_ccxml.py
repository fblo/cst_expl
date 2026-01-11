#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.async.ccxml import CcxmlClient
from cccp.async.protocol import CCCProtocol
from twisted.trial import unittest

import cccp.protocols.messages.user_control as message_user


class CCCProtocolTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = mock.MagicMock()
        self.protocol = CCCProtocol(self.factory)

    def test_init(self):
        self.assertEquals(self.protocol.buffer, [])
        self.assertEquals(self.protocol.version, 1234)
        self.assertEquals(self.protocol.compression_supported, True)
        self.assertEquals(self.protocol.setup, False)
        self.assertEquals(self.protocol.factory, self.factory)

    def test_connectionMade(self):
        self.protocol.sendMessage = mock.MagicMock()
        self.protocol.connectionMade()
        self.protocol.sendMessage.assert_called_once_with(
            self.protocol.factory.module_id,
            self.protocol.version,
            self.protocol.compression_supported
        )

    def test_dataReceived(self):
        self.protocol.factory.module_id = message_user.initialize
        self.protocol.call_factory_method = mock.MagicMock()
        data = ".\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00login\x08\x00\x00\x00password\x01\x00\x00\x00\x00\xd2\x04\x00\x00\x00\x00\x00\x00"
        self.protocol.dataReceived(data)
        self.protocol.call_factory_method.assert_called_once_with(
            'add_session', (
                1, 'login', 'password', 1, False, 1234, ''
            )
        )

    def test_sendMessage(self):
        self.protocol.serialize = mock.MagicMock(return_value="foo")
        self.protocol.transport = mock.MagicMock()

        self.protocol.sendMessage("arg1", "arg2")
        self.protocol.serialize.assert_called_once_with(("arg1", "arg2"))
        self.protocol.transport.write.assert_called_once_with("foo")

    def test_serialize(self):
        self.protocol.factory.module_id = message_user.initialize
        data = (10000, 1, 'login', 'password', 1, False, 1234, '')
        result = self.protocol.serialize(data)
        self.assertEquals(
            result,
            ".\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x05\x00\x00"
            "\x00login\x08\x00\x00\x00password\x01\x00\x00\x00\x00\xd2\x04"
            "\x00\x00\x00\x00\x00\x00"
        )

    def test_call_factory_method(self):
        self.protocol.call_factory_method("method", ["method_data"])
        self.protocol.factory.on_method.assert_called_once_with("method_data")


class CcxmlClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = CcxmlClient("name", "127.0.0.1", 20012)

    def test_init(self):
        self.assertEquals(self.client.name, "name")
        self.assertEquals(self.client.ip, "127.0.0.1")
        self.assertEquals(self.client.port, 20012)
        self.assertEquals(self.client.module_id, message_user.initialize)
        self.assertEquals(self.client.d_connect, None)

    def test_buildProtocol(self):
        self.client.resetDelay = mock.MagicMock()
        result = self.client.buildProtocol("foobar")
        self.assertIsInstance(self.client.protocol, CCCProtocol)
        self.assertEquals(self.client.resetDelay.called, True)
        self.assertIsInstance(result, CCCProtocol)

    def test_connect_dconnect(self):
        self.client.d_connect = 1
        self.assertRaises(Exception, self.client.connect)

    @mock.patch("cccp.async.factory.reactor")
    def test_connect_no_dconnect(self, mock_reactor):
        self.client.connect()
        mock_reactor.connectTCP.assert_called_once_with(
            self.client.ip, self.client.port, self.client
        )

    def test_connection_ok(self):
        self.client.d_connect = mock.MagicMock()
        self.client.on_connection_ok('1234')
        self.client.d_connect.callback.assert_called_once_with(True)

    def test_on_reject(self):
        self.client.get_reject = mock.MagicMock()
        self.client.on_reject("foo", "bar")
        self.client.get_reject.assert_called_once_with("foo", "bar")

    def test_on_server_event(self):
        self.client.get_server_event = mock.MagicMock()
        self.client.on_server_event(
            "session_id", "bs", "bs", "bs", "event_name", "event_object"
        )
        self.client.get_server_event.assert_called_once_with(
            "session_id", "event_name", "event_object"
        )

    def test_on_login_ok(self):
        self.client.get_login_ok = mock.MagicMock()
        self.client.on_login_ok(
            "session_id", "user_id", "explorer_id", "bs", "bs", "bs"
        )
        self.client.get_login_ok.assert_called_once_with(
            "session_id", "user_id", "explorer_id"
        )

    def test_on_logout_ok(self):
        self.client.get_logout_ok = mock.MagicMock()
        self.client.on_logout_ok("session_id")
        self.client.get_logout_ok.assert_called_once_with("session_id")

    def test_connect_done(self):
        self.client.d_connect = 1
        self.client.connect_done("True")
        self.assertEquals(self.client.d_connect, None)

    def test_client_event(self):
        self.client.protocol = mock.MagicMock()
        self.client.client_event(
            "session_id", "source", "target", "event_name", "event_object"
        )
        self.client.protocol.sendMessage.assert_called_once_with(
            message_user.client_event, "session_id", "source",
            "target", 0.0, "event_name", "event_object"
        )

    def test_add_session(self):
        self.client.protocol = mock.MagicMock()
        self.client.add_session("session_id", "login", "password", True)
        self.client.protocol.sendMessage.assert_called_once_with(
            message_user.add_session, "session_id", "login",
            "password", 1, True, self.client.protocol.version,
            ""
        )

    def test_logout(self):
        self.client.protocol = mock.MagicMock()
        self.client.logout("session_id")
        self.client.protocol.sendMessage.assert_called_once_with(
            message_user.logout, "session_id"
        )

    def test_disconnected(self):
        self.client.protocol = mock.MagicMock()
        self.client.disconnected("session_id")
        self.client.protocol.sendMessage.assert_called_once_with(
            message_user.disconnected, "session_id"
        )
