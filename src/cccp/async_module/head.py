#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from twisted.internet import defer

from cccp.async_module.factory import CCCFactory
from cccp.protocols.commons import IncrementIdReservation

import cccp.protocols.messages.explorer as message
import cccp.protocols.messages.base as message_base

from ivcommons.log import Log

log = Log("cccp.async.head")


class HeadClient(CCCFactory, object):
    def __init__(self, name, ip, port=20000):
        super(HeadClient, self).__init__(name, ip, port)
        self.log = log
        self.inc_id = IncrementIdReservation()
        self.module_id = message.initialize
        self.deferreds = {}
        self.d_connect = None

    def has_configuration_changed(self, vocal_host, port=20000):
        return super(HeadClient, self).has_configuration_changed(vocal_host, port)

    def on_connection_ok(self, server_version, server_date):
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        raise Exception(message.LOGIN_FAILED % reason)

    def on_use_default_namespaces_index_ok(self):
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)

        self.connection_finished()

    def get_object(self, path):
        deferred, query_id = self.prepare_query(self.get_object_done)
        self.protocol.sendMessage(
            message.query_node_object_content, 1, query_id, path, False, True, ""
        )
        self.protocol.sendMessage(message.stop_query, 1, query_id)
        return deferred

    def on_get_object_done(self, query_id, obj, result):
        self.deferreds[query_id].callback((query_id, result, obj))

    def get_object_done(self, result_tuple):
        query_id, result, obj = result_tuple
        del self.deferreds[query_id]
        return obj

    def get_children(self, path):
        deferred, query_id = self.prepare_query(self.get_children_done)
        self.protocol.sendMessage(message.query_node_children, 1, query_id, path)
        self.protocol.sendMessage(message.stop_query, 1, query_id)
        return deferred

    def on_get_children_done(self, query_id, obj, result):
        self.deferreds[query_id].callback((query_id, result, obj))

    def get_children_done(self, result_tuple):
        query_id, result, obj = result_tuple
        if result != 0:
            raise Exception(message_base.NONE_RESULT)
        del self.deferreds[query_id]
        return obj.nodes

    def on_node_children_response(self, session_id, system_id, obj, result):
        self.on_get_children_done(system_id, obj, result)

    def on_node_raw_object_content_response(
        self, session_id, system_id, obj, uncompressed_size, result
    ):
        self.on_get_object_done(system_id, obj, result)

    def prepare_query(self, callback, errback=None):
        query_id = self.inc_id.reserve()
        d = defer.Deferred()
        self.deferreds[query_id] = d
        d.addCallback(callback)
        return d, query_id

    @defer.inlineCallbacks
    def list(self, path):
        result = []
        nodes = yield self.get_children(path)
        for node in nodes:
            result.append(node.name)

        defer.returnValue(result)

    @defer.inlineCallbacks
    def get(self, path):
        o = yield self.get_object(path)
        defer.returnValue(o)
