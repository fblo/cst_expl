#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2017
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from twisted.internet import reactor, defer

from cccp.async_module.protocol import CCCProtocol
from ivcommons.factory import IVReconnectingClientFactory
from ivcommons.log import Log

log = Log("cccp.async.factory")


class CCCFactory(IVReconnectingClientFactory, object):
    def __init__(self, name, ip, port):
        super(CCCFactory, self).__init__(name, ip, port)
        self.d_connect = None

    def has_configuration_changed(self, vocal_host, port):
        return self.ip != vocal_host or self.port != port

    def end_connection(self, project_key):
        super(CCCFactory, self).end_connection(self.name, project_key)

    def buildProtocol(self, addr):
        self.log.system_message(
            "%s protocol created on '%s:%s'."
            % (self.__class__.__name__, self.ip, self.port)
        )
        self.protocol = CCCProtocol(self)
        self.resetDelay()
        return self.protocol

    def connect(self):
        if self.d_connect is not None:
            raise Exception("There is already a connection attempt.")

        self.d_connect = defer.Deferred()
        self.d_connect.addCallback(self.connect_done)
        reactor.connectTCP(self.ip, self.port, self)
        return self.d_connect

    def connect_done(self, result_value):
        del self.d_connect
        self.d_connect = None
        return result_value

    def on_server_ask_to_disconnect(self):
        if self.protocol and self.protocol.transport:
            self.protocol.transport.loseConnection()
