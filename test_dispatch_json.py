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
            "calls": [],
            "call_history": [],
            "call_details": [],
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
            # Get all communication tasks (including completed ones)
            self.communication_task_view_idx = self.start_view(
                "tasks",
                "communications_tasks",
                self._communication_task_xqueries_list,
                "",
            )
            # Get all communication sessions (including terminated)
            self.communication_session_view_idx = self.start_view(
                "comm_sessions",
                "communications_sessions",
                self._communication_session_xqueries_list,
                "",
            )
            # Get all communication queues (including terminated)
            self.communication_queue_view_idx = self.start_view(
                "comm_queues",
                "communications_queues",
                self._communication_queue_xqueries_list,
                "",
            )
            # Also get outbound communications for complete picture
            self.outbound_comm_view_idx = self.start_view(
                "outbound",
                "outbound_communication_sessions",
                self._outbound_communication_session_xqueries_list,
                "",
            )

    def extract_all_data(self):
        """Extrait toutes les donnees apres un delai"""
        view_data = {}

        view_configs = [
            ("users", self.user_view_idx, self._user_xqueries_list),
            ("queues", self.queue_view_idx, self._service_xqueries_list),
            (
                "comm_sessions",
                self.communication_session_view_idx,
                self._communication_session_xqueries_list,
            ),
            (
                "tasks",
                self.communication_task_view_idx,
                self._communication_task_xqueries_list,
            ),
            (
                "comm_queues",
                self.communication_queue_view_idx,
                self._communication_queue_xqueries_list,
            ),
            (
                "outbound",
                self.outbound_comm_view_idx,
                self._outbound_communication_session_xqueries_list,
            ),
        ]

        for view_name, view_idx, fields in view_configs:
            if view_idx is None:
                continue
            try:
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

                view_data[view_name] = items
                print(f"DEBUG: {view_name}: {len(items)} items")

            except Exception as e:
                print(f"DEBUG: Error fetching {view_name}: {e}")
                self.result["error"] = str(e)

        # Build comprehensive call history
        call_history = []

        # Index queue details by session_id for quick lookup
        queue_by_session = {}
        for q in view_data.get("comm_queues", []):
            session_id = q.get("session.session_id", "")
            if session_id:
                queue_by_session[session_id] = q

        # Index outbound calls by session_id
        outbound_by_session = {}
        for o in view_data.get("outbound", []):
            session_id = o.get("session_id", "")
            if session_id:
                outbound_by_session[session_id] = o

        # Process tasks (completed calls)
        for task in view_data.get("tasks", []):
            task_id = task.get("task_id", "")
            parent_session_id = task.get("parent_call_session_id", "")
            start_date = task.get("start_date", "")
            end_date = task.get("end_date", "")
            stop_waiting_date = task.get("stop_waiting_date", "")
            management_date = task.get("management_date", "")

            # Calculate durations
            durations = self.calculate_durations(
                start_date, end_date, stop_waiting_date, management_date
            )

            # Get phone numbers from queue details
            queue_info = queue_by_session.get(parent_session_id, {})
            remote_number = queue_info.get("attributes.remote_number.value", "")
            local_number = queue_info.get("attributes.local_number.value", "")

            # Also check outbound data
            outbound_info = outbound_by_session.get(parent_session_id, {})
            if not remote_number:
                remote_number = outbound_info.get("last_outbound_call_target.value", "")

            call_entry = {
                "task_id": task_id,
                "parent_session_id": parent_session_id,
                "queue_type": task.get("queue_type", ""),
                "queue_display_name": task.get("queue_display_name", ""),
                "start_date": start_date,
                "end_date": end_date,
                "stop_waiting_date": stop_waiting_date,
                "management_date": management_date,
                "post_management_date": task.get("post_management_date", ""),
                "manager_login": task.get("manager_session.user.login", ""),
                "manager_profile": task.get("manager_session.profile_name", ""),
                # Phone numbers
                "caller": remote_number,  # Appelant
                "callee": local_number,  # Appelé
                # Durations
                "waiting_duration": durations["waiting"],
                "managing_duration": durations["managing"],
                "post_management_duration": durations["post_management"],
                "total_duration": durations["total"],
            }

            # Add outbound-specific fields
            if outbound_info:
                call_entry["outbound_state"] = outbound_info.get(
                    "outbound_state.value", ""
                )
                call_entry["total_legs"] = outbound_info.get(
                    "total_leg_count.value", ""
                )
                call_entry["contacted_legs"] = outbound_info.get(
                    "contacted_leg_count.value", ""
                )

            call_history.append(call_entry)

        # Process outbound calls as well
        for outbound in view_data.get("outbound", []):
            session_id = outbound.get("session_id", "")

            # Check if already processed via tasks
            already_processed = any(
                c.get("parent_session_id") == session_id for c in call_history
            )
            if already_processed:
                continue

            start_date = outbound.get("last_outbound_call_start.value", "")
            end_date = outbound.get("terminate_date", "")
            contact_start = outbound.get("last_outbound_call_contact_start.value", "")

            durations = self.calculate_durations(
                start_date, end_date, contact_start, contact_start
            )

            call_entry = {
                "task_id": outbound.get("outbound_call_id.value", ""),
                "parent_session_id": session_id,
                "queue_type": "outbound",
                "queue_display_name": outbound.get("user.name", ""),
                "start_date": start_date,
                "end_date": end_date,
                "manager_login": outbound.get("user.login", ""),
                "manager_profile": outbound.get("profile_name", ""),
                "caller": outbound.get("user.name", ""),  # Agent making the call
                "callee": outbound.get("last_outbound_call_target.value", ""),  # Target
                "waiting_duration": "0s",
                "managing_duration": durations["managing"],
                "post_management_duration": "0s",
                "total_duration": durations["total"],
                "outbound_state": outbound.get("outbound_state.value", ""),
            }

            call_history.append(call_entry)

        # Sort by start date descending
        call_history.sort(key=lambda x: x.get("start_date", ""), reverse=True)

        self.result["users"] = view_data.get("users", [])
        self.result["queues"] = view_data.get("queues", [])
        self.result["calls"] = view_data.get("comm_sessions", [])
        self.result["call_history"] = call_history

        self.output_result()

    def on_view_list_ok(self, view_idx, view_name, object_list, complete):
        pass

    def calculate_durations(
        self, start_date, end_date, stop_waiting_date, management_date
    ):
        """Calcule les durées à partir des dates ISO 8601"""

        def format_duration(seconds):
            if seconds <= 0:
                return "0s"
            elif seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                return f"{seconds // 60}m{seconds % 60}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h{minutes}m"

        def parse_date(date_str):
            if not date_str or date_str == "None" or date_str == "":
                return None
            try:
                # Handle ISO format with or without timezone
                if date_str.endswith("Z"):
                    date_str = date_str[:-1] + "+00:00"
                return datetime.fromisoformat(date_str)
            except:
                return None

        start = parse_date(start_date)
        end = parse_date(end_date)
        stop_waiting = parse_date(stop_waiting_date)
        management = parse_date(management_date)

        waiting = 0
        managing = 0
        post_management = 0
        total = 0

        if start:
            if stop_waiting:
                waiting = int((stop_waiting - start).total_seconds())
            if management:
                managing = int((end - management).total_seconds()) if end else 0
            if end:
                total = int((end - start).total_seconds())

        return {
            "waiting": format_duration(waiting),
            "managing": format_duration(managing),
            "post_management": format_duration(post_management),
            "total": format_duration(total),
        }

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
            "calls": [],
            "call_history": [],
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

        for c in self.result.get("calls", []):
            call = {}
            for k, v in c.items():
                call[k] = serialize(v)
            result["calls"].append(call)

        for h in self.result.get("call_history", []):
            history = {}
            for k, v in h.items():
                history[k] = serialize(v)
            result["call_history"].append(history)

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
