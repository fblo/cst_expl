#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test pour interroger le dispatch CCCP et sortir en JSON
# Usage: python3 test_dispatch_json.py <ip> <port>

import sys
import json
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class JSONDispatchClient(DispatchClient):
    def __init__(self, name, ip, port):
        super(JSONDispatchClient, self).__init__(name, ip, port)
        self.result = {
            "users": [],
            "queues": [],
            "calls_inbound": [],
            "calls_outbound": [],
            "calls_history": [],
            "error": None,
        }

    def on_connection_ok(self, server_version, server_date):
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        self.result["error"] = f"Login failed: {reason}"
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()
        reactor.callLater(2, self.extract_all_data)

    def connect_done(self, result_value):
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
                ".[group/path eq '/default' or sessions/last/session/profile_name eq 'Superviseur_default']",
            )
            self.communication_session_view_idx = self.start_view(
                "comm_sessions",
                "sessions",
                self._communication_session_xqueries_list,
                ".[session_type ne 3 and terminate_date eq '']",
            )
            self.outbound_communication_session_view_idx = self.start_view(
                "outbound_sessions",
                "sessions",
                self._outbound_communication_session_xqueries_list,
                ".[session_type eq 3 and terminate_date eq '']",
            )
            # Taches de communication
            self.communication_task_view_idx = self.start_view(
                "tasks",
                "communications_tasks",
                self._communication_task_xqueries_list,
                "",
            )
            # Appels historiques (terminés aujourd'hui)
            today = datetime.now().strftime("%Y/%m/%d 00:00:00")
            self.communication_session_history_view_idx = self.start_view(
                "comm_history",
                "sessions",
                self._communication_session_xqueries_list,
                f".[session_type ne 3 and terminate_date gt '{today}']",
            )
            self.outbound_communication_session_view_idx = self.start_view(
                "outbound_sessions",
                "outbound_communications_sessions",
                self._outbound_communication_session_xqueries_list,
                "",
            )
            # Taches de communication
            self.communication_task_view_idx = self.start_view(
                "tasks",
                "communications_tasks",
                self._communication_task_xqueries_list,
                "",
            )
            # Appels historiques (terminés aujourd'hui)
            today = datetime.now().strftime("%Y/%m/%d 00:00:00")
            self.communication_session_history_view_idx = self.start_view(
                "comm_history",
                "communications_sessions",
                self._communication_session_xqueries_list,
                f".[session_id ne '' and terminate_date gt '{today}']",
            )

    def extract_all_data(self):
        """Extrait toutes les donnees apres un delai"""
        for view_name in [
            "users",
            "queues",
            "comm_sessions",
            "outbound_sessions",
            "comm_tasks",
            "comm_history",
        ]:
            try:
                if view_name == "users":
                    view_idx = self.user_view_idx
                    fields = self._user_xqueries_list
                elif view_name == "queues":
                    view_idx = self.queue_view_idx
                    fields = self._service_xqueries_list
                elif view_name == "comm_sessions":
                    view_idx = self.communication_session_view_idx
                    fields = self._communication_session_xqueries_list
                elif view_name == "outbound_sessions":
                    view_idx = self.outbound_communication_session_view_idx
                    fields = self._outbound_communication_session_xqueries_list
                elif view_name == "comm_tasks":
                    view_idx = self.communication_task_view_idx
                    fields = self._communication_task_xqueries_list
                elif view_name == "comm_history":
                    view_idx = self.communication_session_history_view_idx
                    fields = self._communication_session_xqueries_list
                else:
                    continue

                view = self.tables[view_idx][0]
                items = []

                for obj_id, obj_data in view.items():
                    if obj_data and isinstance(obj_data, list):
                        item = {"id": obj_id}
                        for i, value in enumerate(obj_data):
                            if i < len(fields):
                                field_name = fields[i]
                                if isinstance(value, bytes):
                                    try:
                                        value = value.decode("utf-8")
                                    except:
                                        pass
                                item[field_name] = value
                        items.append(item)

                if view_name == "users":
                    self.result["users"] = items
                elif view_name == "queues":
                    self.result["queues"] = items
                elif view_name == "comm_sessions":
                    self.result["calls_inbound"] = items
                elif view_name == "outbound_sessions":
                    self.result["calls_outbound"] = items
                elif view_name == "comm_tasks":
                    self.result["calls_tasks"] = items
                elif view_name == "comm_history":
                    self.result["calls_history"] = items

            except Exception as e:
                self.result["error"] = str(e)

        self.output_result()

    def on_view_list_ok(self, view_idx, view_name, object_list, complete):
        pass

    def output_result(self):
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, bytes):
                try:
                    return obj.decode("utf-8")
                except:
                    return str(obj)
            return str(obj)

        result = {
            "users": [],
            "queues": [],
            "calls_inbound": [],
            "calls_outbound": [],
            "calls_history": [],
            "error": self.result.get("error"),
        }

        for u in self.result.get("users", []):
            user = {}
            for k, v in u.items():
                user[k] = serialize(v)
            result["users"].append(user)

        for q in self.result.get("queues", []):
            queue = {}
            for k, v in q.items():
                queue[k] = serialize(v)
            result["queues"].append(queue)

        for c in self.result.get("calls_inbound", []):
            call = {}
            for k, v in c.items():
                call[k] = serialize(v)
            result["calls_inbound"].append(call)

        for c in self.result.get("calls_outbound", []):
            call = {}
            for k, v in c.items():
                call[k] = serialize(v)
            result["calls_outbound"].append(call)

        for c in self.result.get("calls_history", []):
            call = {}
            for k, v in c.items():
                call[k] = serialize(v)
            result["calls_history"].append(call)

        print(json.dumps(result, indent=2))
        self.stop()

    def stop(self):
        try:
            self.protocol.transport.loseConnection()
        except:
            pass
        reactor.stop()


def test_dispatch_json(ip="10.199.30.67", port=20103):
    client = JSONDispatchClient("dispatch_json", ip, port)
    client.connect()
    reactor.run()


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20103
    test_dispatch_json(ip, port)
