#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from datetime import datetime

from cccp.async_module.factory import CCCFactory
from cccp.protocols.dispatch import BaseDispatchClient

import cccp.protocols.messages.explorer as message

from ivcommons.log import Log

log = Log("cccp.async.dispatch")


class DispatchClient(CCCFactory, BaseDispatchClient):
    def __init__(self, name, ip, port, reset_time=None, is_callflow=False):
        super(DispatchClient, self).__init__(name, ip, port)
        BaseDispatchClient.__init__(self, reset_time, is_callflow)
        self.log = log
        self.module_id = message.initialize
        self.is_callflow = is_callflow
        self.current_daily_outbound_xquery_filters = (
            ".[session_type eq 3 and terminate_date gt '%s' "
            "and profile_name ne 'Superviseur_default' "
            "and user/group/path eq '/default']"
            % datetime.now().strftime("%Y/%m/%d 00:00:00")
        )

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

    def connect_done(self, result_value):
        del self.d_connect
        self.d_connect = None
        if not self.is_callflow:
            self.queue_view_idx = self.start_view(
                "queues",
                "queues",
                self._service_xqueries_list,
                ".[virtual_queue eq 0 and running]",
            )
            self.user_view_idx = self.start_view(
                "users",
                "users",
                self._user_xqueries_list,
                ".[sessions/last/session/profile_name "
                "ne 'Superviseur_default' and group/path eq '/default' "
                "or login eq 'consistent']",
            )
            self.communication_session_view_idx = self.start_view(
                "sessions",
                "communications_sessions",
                self._communication_session_xqueries_list,
                ".[connections/last/call_id ne '' and session_type ne 3]",
            )
            self.outbound_daily_communication_session_view_idx = self.start_view(
                "sessions",
                "outbound_daily_communications_sessions",
                self._outbound_daily_communication_session_xqueries_list,
                self.current_daily_outbound_xquery_filters,
            )
            self.outbound_communication_session_view_idx = self.start_view(
                "sessions",
                "outbound_communications_sessions",
                self._outbound_communication_session_xqueries_list,
                ".[session_type eq 3 and terminate_date eq '' "
                "and profile_name ne 'Superviseur_default' "
                "and user/group/path eq '/default']",
            )
            self.communication_queue_view_idx = self.start_view(
                "file_tasks",
                "communications_queues",
                self._communication_queue_xqueries_list,
                ".[terminate_date eq '']",
            )
            self.communication_task_view_idx = self.start_view(
                "tasks",
                "communications_tasks",
                self._communication_task_xqueries_list,
                "",
            )
        else:
            log.debug("Dispatch setup for callflow usage.")
            self.user_view_idx = self.start_view(
                "users",
                "users",
                self._user_xqueries_list_callflow,
                ".[sessions/last/session/profile_name "
                "ne 'Superviseur_default' and group/path eq '/default' "
                "or login eq 'consistent']",
            )
            self.communication_session_view_idx = self.start_view(
                "sessions",
                "communications_sessions",
                self._communication_session_xqueries_list_callflow,
                ".[connections/last/call_id ne '' and session_type ne 3]",
            )

        return result_value

    def query_list(self, idx, db_root, filter):
        self.protocol.sendMessage(
            message.query_list, 1, idx, "/dispatch", 0, db_root, filter, 0, "", 0
        )

    def query_object(self, idx, id, format_id, obj_id):
        self.protocol.sendMessage(
            message.query_object, 1, idx, "/dispatch", id, format_id, obj_id
        )

    def stop_query(self, idx):
        self.protocol.sendMessage(message.stop_query, 1, idx)

    def set_object_format(self, cst_format):
        self.protocol.sendMessage(message.set_object_format, 1, cst_format)
