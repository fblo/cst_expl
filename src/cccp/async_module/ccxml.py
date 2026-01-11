#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from cccp.async_module.factory import CCCFactory
from cccp.protocols.ccxml import BaseCcxmlClient

import cccp.protocols.messages.user_control as message_user
import cccp.protocols.messages.base as message_base

from ivcommons.log import Log

log = Log("cccp.async.ccxml")


class CcxmlClient(CCCFactory, BaseCcxmlClient):
    def __init__(self, name, ip, port):
        super(CcxmlClient, self).__init__(name, ip, port)
        self.log = log
        self.d_connect = None
        self.module_id = message_user.initialize
        self.connected_sessions = {}
        self.connecting_sessions = {}

    def on_connection_ok(self, server_version):
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()

    def on_reject(self, session_id, reason):
        if reason == "Agent déjà loggué":
            reason = message_base.USER_ALREADY_CONNECTED

        elif reason.startswith("Utilisateur"):
            if reason.endswith("non trouvé"):
                reason = message_base.USER_NOT_FOUND

            if reason.endswith("non actif"):
                reason = message_base.USER_NOT_ACTIVE

        self.get_reject(session_id, reason)

    def on_server_event(
        self, session_id, source, target, delay, event_name, event_object
    ):
        self.get_server_event(session_id, event_name, event_object)

    def on_login_ok(
        self, session_id, user_id, explorer_id, interface_name, so_mark, tos
    ):
        self.get_login_ok(session_id, user_id, explorer_id)
        if session_id in self.connecting_sessions:
            self.connected_sessions[session_id] = self.connecting_sessions.pop(
                session_id
            )

    def on_needs_control(self, session_id, mandatory):
        self.protocol.sendMessage(message_user.control_ok, session_id)

    def on_reply_values(self, session_id, object, user_id, explorer_id, interface_name):
        self.get_reject(session_id, message_base.USER_ALREADY_CONNECTED)

    def on_logout_ok(self, session_id):
        self.get_logout_ok(session_id)
        self.connected_sessions.pop(session_id, None)

    def connect_done(self, result_value):
        del self.d_connect
        self.d_connect = None
        for sid in self.connected_sessions.keys():
            self.add_session(sid, *self.connected_sessions.pop(sid))
        return result_value

    def client_event(self, session_id, source, target, event_name, event_object):
        self.protocol.sendMessage(
            message_user.client_event,
            session_id,
            source,
            target,
            0.0,
            event_name,
            event_object,
        )

    def add_session(self, session_id, login, password, was_connected):
        self.protocol.sendMessage(
            message_user.add_session,
            session_id,
            login,
            password,
            1,
            was_connected,
            self.protocol.version,
            "",
        )
        self.connecting_sessions[session_id] = (login, password, was_connected)

    def logout(self, session_id):
        self.protocol.sendMessage(message_user.logout, session_id)

    def disconnected(self, session_id):
        self.protocol.sendMessage(message_user.disconnected, session_id)

    def set_can_disconnect(self, session_id, value=True):
        # This event is used to force the server to send the event
        # 'needs_control'
        self.protocol.sendMessage(message_user.set_can_disconnect, session_id, value)

    def needs_context(self, session_id):
        # This event is used to ask the context of a session,
        # the answer will be sent on 'reply_values'
        self.protocol.sendMessage(
            message_user.needs_context, session_id, "", self.protocol.version, 1
        )
