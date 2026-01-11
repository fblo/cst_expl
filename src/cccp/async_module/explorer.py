#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2017
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from twisted.internet import defer

from cccp.async_module.factory import CCCFactory

import cccp.protocols.messages.explorer as message_explorer

from ivcommons.log import Log

log = Log("cccp.async.explorer")


class ExplorerClient(CCCFactory, object):
    def __init__(self, name, ip, port):
        super(ExplorerClient, self).__init__(name, ip, port)
        self.log = log
        self.d_connect = None
        self.module_id = message_explorer.initialize
        self.deferred = None

    def on_connection_ok(self, server_version, server_date):
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()

    def send_event(self, event_name, event_object=None):
        self.protocol.sendMessage(
            message_explorer.client_event, 1, "", "", "", 0.0, event_name, event_object
        )

    def on_server_event(
        self, session_id, source, target, delay, event_name, event_object
    ):
        try:
            event_name = "on_" + event_name.split("com.consistent.explorer.")[
                1
            ].replace(".", "_")
            getattr(self, event_name)(event_object)

        except:
            log.error("Server call error: %s(%s)" % (event_name, (repr(event_object))))

    def kill_session(self, user_id):
        self.send_event("com.consistent.explorer.kill_session.%s" % user_id)
        self.deferred = defer.Deferred()
        self.deferred.addCallback(self.kill_session_done)
        return self.deferred

    def on_session_not_found(self, *args, **kwargs):
        self.deferred.callback(False)

    def on_session_killed(self, *args, **kwargs):
        self.deferred.callback(True)

    def kill_session_done(self, value):
        return value
