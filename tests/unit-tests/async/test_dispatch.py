#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.async.dispatch import DispatchClient
from cccp.async.protocol import CCCProtocol
from twisted.trial import unittest

import cccp.protocols.messages.explorer as message


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
        self.protocol.factory.module_id = message.initialize
        self.protocol.call_factory_method = mock.MagicMock()
        data = "&\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00login\x08\x00\x00\x00password\x01\x00\x00\x00\x00" # NOQA
        self.protocol.dataReceived(data)
        self.protocol.call_factory_method.assert_called_once_with(
            'login', (1, 'login', 'password', 1, False)
        )

    def test_sendMessage(self):
        self.protocol.serialize = mock.MagicMock(return_value="foo")
        self.protocol.transport = mock.MagicMock()

        self.protocol.sendMessage("arg1", "arg2")
        self.protocol.serialize.assert_called_once_with(("arg1", "arg2"))
        self.protocol.transport.write.assert_called_once_with("foo")

    def test_serialize(self):
        self.protocol.factory.module_id = message.initialize
        data = (10000, 1, 'login', 'password', 1, False, 1234, '')
        result = self.protocol.serialize(data)
        self.assertEquals(
            result, "&\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x05"
            "\x00\x00\x00login\x08\x00\x00\x00password\x01\x00\x00\x00\x00"
        )

    def test_call_factory_method(self):
        self.protocol.call_factory_method("method", ["method_data"])
        self.protocol.factory.on_method.assert_called_once_with("method_data")


class DispatchClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = DispatchClient("name", "127.0.0.1", 20012)

    def test_init(self):
        self.assertEquals(self.client.ip, "127.0.0.1")
        self.assertEquals(self.client.port, 20012)
        self.assertEquals(self.client.module_id, message.initialize)
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

    def test_on_connection_ok(self):
        self.client.protocol = mock.MagicMock()
        self.client.on_connection_ok('1234', "date")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.login, 1, "admin", "admin", 0, False
        )

    def test_on_login_ok(self):
        self.client.protocol = mock.MagicMock()
        self.client.on_login_ok("session_id", "user_id", "explorer_id")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.use_default_namespaces_index
        )

    def test_on_login_failed(self):
        self.assertRaises(
            Exception, self.client.on_login_failed, "session_id", "reason"
        )

    def test_on_use_default_namespaces_index_ok(self):
        self.client.d_connect = mock.MagicMock()
        self.client.on_use_default_namespaces_index_ok()
        self.client.d_connect.callback.assert_called_once_with(True)

    def test_connect_done(self):
        self.client.start_view = mock.MagicMock()
        self.client.d_connect = True
        result = self.client.connect_done(True)
        self.assertEquals(self.client.d_connect, None)
        self.assertEquals(result, True)
        self.assertEquals(self.client.start_view.call_count, 7)

    def test_query_list(self):
        self.client.protocol = mock.MagicMock()
        self.client.query_list("idx", "db_root", "filter")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.query_list, 1, "idx", "/dispatch", 0, "db_root",
            "filter", 0, "", 0
        )

    def test_query_object(self):
        self.client.protocol = mock.MagicMock()
        self.client.query_object("idx", "id", "format_id", "obj_id")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.query_object, 1, "idx", "/dispatch", "id",
            "format_id", "obj_id"
        )

    def test_stop_query(self):
        self.client.protocol = mock.MagicMock()
        self.client.stop_query("idx")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.stop_query, 1, "idx"
        )

    def test_set_object_format(self):
        self.client.protocol = mock.MagicMock()
        self.client.set_object_format("cst_format")
        self.client.protocol.sendMessage.assert_called_once_with(
            message.set_object_format, 1, "cst_format"
        )
