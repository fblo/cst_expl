#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.async.head import HeadClient
from cccp.async.protocol import CCCProtocol
from cccp.protocols.commons import IncrementIdReservation
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
            'login', (
                1, 'login', 'password', 1, False
            )
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
            result, "&\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x05\x00\x00"
            "\x00login\x08\x00\x00\x00password\x01\x00\x00\x00\x00"
        )

    def test_call_factory_method(self):
        self.protocol.call_factory_method("method", ["method_data"])
        self.protocol.factory.on_method.assert_called_once_with("method_data")


class HeadClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = HeadClient("name", "127.0.0.1", 20012)

    def test_init(self):
        self.assertEquals(self.client.name, "name")
        self.assertEquals(self.client.ip, "127.0.0.1")
        self.assertEquals(self.client.port, 20012)
        self.assertEquals(self.client.module_id, message.initialize)
        self.assertEquals(self.client.deferreds, {})
        self.assertEquals(self.client.d_connect, None)
        self.assertIsInstance(self.client.inc_id, IncrementIdReservation)

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
            Exception, self.client.on_login_failed,
            "session_id", "reason"
        )

    def test_on_use_default_namespaces_index_ok(self):
        self.client.d_connect = mock.MagicMock()
        self.client.on_use_default_namespaces_index_ok()
        self.client.d_connect.callback.assert_called_once_with(True)

    def test_connect_done(self):
        self.client.d_connect = True
        result = self.client.connect_done(True)
        self.assertEquals(self.client.d_connect, None)
        self.assertEquals(result, True)

    def test_get_object(self):
        self.client.protocol = mock.MagicMock()
        self.client.prepare_query = mock.MagicMock(
            return_value = ("deferred", "query_id")
        )
        result = self.client.get_object("path")
        self.assertEquals(
            self.client.protocol.sendMessage.call_args_list,
            [
                mock.call(10008, 1, 'query_id', 'path', False, True, ''),
                mock.call(10013, 1, 'query_id')
            ]
        )
        self.assertEquals(result, "deferred")

    def test_on_get_object_done(self):
        self.client.deferreds["query_id"] = mock.MagicMock()
        self.client.on_get_object_done("query_id", "obj", "result")
        self.client.deferreds["query_id"].callback.assert_called_once_with(
            ("query_id", "result", "obj")
        )

    def test_get_object_done(self):
        tuple = ("query_id", 0, 1)
        self.client.deferreds["query_id"] = "truc"
        result = self.client.get_object_done(tuple)

        self.assertEquals("query_id" in self.client.deferreds, False)
        self.assertEquals(result, 1)

    def test_get_children(self):
        self.client.protocol = mock.MagicMock()
        self.client.prepare_query = mock.MagicMock(
            return_value=("deferred", "query_id")
        )
        result = self.client.get_children("path")
        self.assertEquals(
            self.client.protocol.sendMessage.call_args_list,
            [
                mock.call(10009, 1, 'query_id', 'path'),
                mock.call(10013, 1, 'query_id')
            ]
        )
        self.assertEquals(result, "deferred")

    def test_on_get_children_done(self):
        self.client.deferreds["query_id"] = mock.MagicMock()
        self.client.on_get_children_done("query_id", "obj", "result")
        self.client.deferreds["query_id"].callback.assert_called_once_with(
            ("query_id", "result", "obj")
        )

    def test_get_children_done_ok(self):
        obj = mock.MagicMock()
        obj.nodes = 1
        tuple = ("query_id", 0, obj)
        self.client.deferreds["query_id"] = "truc"
        result = self.client.get_children_done(tuple)

        self.assertEquals("query_id" in self.client.deferreds, False)
        self.assertEquals(result, 1)

    def test_get_children_done_fail(self):
        tuple = ("query_id", 1, "obj")
        self.assertRaises(Exception, self.client.get_children_done, tuple)

    def test_on_node_children_response(self):
        self.client.on_get_children_done = mock.MagicMock()
        self.client.on_node_children_response(
            "session_id", "system_id", "obj", "result"
        )
        self.client.on_get_children_done.assert_called_once_with(
            "system_id", "obj", "result"
        )

    def test_on_node_raw_object_content_response(self):
        self.client.on_get_object_done = mock.MagicMock()
        self.client.on_node_raw_object_content_response(
            "session_id", "system_id", "obj", "uncompressed_size", "result"
        )
        self.client.on_get_object_done.assert_called_once_with(
            "system_id", "obj", "result"
        )

    @mock.patch("cccp.async.head.defer.Deferred")
    def test_prepare_query(self,  mock_deferred):
        self.client.deferreds = {}
        self.client.inc_id = mock.MagicMock()
        self.client.inc_id.reserve.return_value = 1
        result1, result2 = self.client.prepare_query("callb", "errb")
        self.assertEquals(self.client.inc_id.reserve.called, True)
        self.assertEquals(result2, 1)
        self.assertEquals(self.client.deferreds[result2], result1)

    def test_list(self):
        node = mock.MagicMock()
        node.name = "foo"
        self.client.get_children = mock.MagicMock(result_value=[node])
        self.client.list("path")
        self.client.get_children.assert_called_once_with("path")

    def test_get(self):
        self.client.get_object = mock.MagicMock(result_value="foo")
        self.client.get("path")
        self.client.get_object.assert_called_once_with("path")
