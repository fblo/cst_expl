#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message

PROJECT = "MPU_PREPROD"


def format_date_to_second(date_str):
    if not date_str or date_str in ("", "None"):
        return ""
    try:
        if isinstance(date_str, bytes):
            date_str = date_str.decode("utf-8")
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(date_str)


def clean_string(value):
    """Convert bytes to string and clean up"""
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    value = str(value).strip()
    value = value.strip("b'").strip("'").strip('"').strip('"')
    return value


def format_session_type(session_type):
    if session_type == "1" or session_type == 1:
        return "incoming"
    elif session_type == "3" or session_type == 3:
        return "outgoing"
    return str(session_type)


def is_call_session(session_id):
    if session_id and isinstance(session_id, str):
        return session_id.startswith("session_") or "session_" in session_id
    return False


def is_agent_session(session_id):
    if session_id and isinstance(session_id, str):
        return session_id.startswith("user_") or "user_" in session_id
    return False


class ProjectDispatchClient(DispatchClient):
    def __init__(self, name, ip, port, project):
        super(ProjectDispatchClient, self).__init__(name, ip, port)
        self.project = project
        self.db_path = f"/dispatch_{project}"

        self._user_xqueries_list = sorted(
            [
                "login",
                "name",
                "contact_duration.max('0')",
                "hold_duration.max('0')",
                "ringing_duration.max('0')",
                "state_group_pause.duration('0')",
                "state_group_outbound.duration('0')",
                "states.last.state.start_date",
                "last_state_display_name",
                "last_state_name",
                "last_state_date",
                "last_task_display_name",
                "last_task_name",
                "tasks.last.task.start_date",
                "tasks.last.task.management_effective_date",
                "tasks.last.task.end_date",
                "total_inbound.count('0')",
                "lost_inbound.count('0')",
                "managed_inbound.count('0')",
                "total_tasks.count('0')",
                "transferred_inbound.count('0')",
                "redirected_inbound.count('0')",
                "task_state_held.duration('0')",
                "task_state_ringing.duration('0')",
                "task_state_contact.duration('0')",
                "sessions.last.session.login_date",
                "sessions.last.session.logout_date",
                "sessions.last.session.profile_name",
                "sessions.last.session.session_id",
                "sessions.last.session.last_record.value",
                "sessions.last.session.record_active.value",
                "sessions.last.session.current_spies.value",
                "sessions.last.session.current_mode",
                "sessions.last.session.phone_uri",
                "sessions.last.session.logged",
                "busy_count",
            ]
        )

        self._service_xqueries_list = sorted(
            [
                "name",
                "display_name",
                "latent_sessions_count",
                "logged_sessions_count",
                "working_sessions_count",
                "withdrawn_sessions_count",
                "outbound_sessions_count",
                "supervision_sessions_count",
                "running_tasks_count",
                "waiting_tasks_count",
                "contact_duration.count('0')",
                "waiting_duration.count('0')",
                "max_waiting_time_threshold.count('0')",
                "max_estimated_waiting_time_threshold.count('0')",
                "not_manageable_with_latent_users.count('0')",
                "not_manageable_without_latent_users.count('0')",
                "managed_tasks.count('0')",
                "failed_tasks.count('0')",
                "oldest_contact_date",
                "contact_duration.max('0')",
                "oldest_waiting_date",
                "waiting_duration.max('0')",
            ]
        )

        self._communication_session_xqueries_list = sorted(
            [
                "create_date",
                "session_type",
                "session_id",
                "terminate_date",
                "user.login",
                "user.name",
                "manager_session.user.login",
                "manager_session.profile_name",
                "queue_name",
                "attributes.local_number.value",
                "attributes.remote_number.value",
                "start_date",
                "management_effective_date",
                "last_record.value",
                "record_active.value",
            ]
        )

    def on_list_response(self, session_id, idx, object):
        super(ProjectDispatchClient, self).on_list_response(session_id, idx, object)
        super(ProjectDispatchClient, self).on_list_response(session_id, idx, object)

    def on_object_response(self, session_id, idx, object, obj_id):
        if idx == getattr(self, "sessions_view_idx", None):
            view = self.tables[idx][0]
            if hasattr(object, "values"):
                for e in object.values:
                    if hasattr(e, "value") and hasattr(e, "field_index"):
                        field_name = self.xqueries_tables.get(
                            "communications_sessions", {}
                        ).get(e.field_index)
                        if field_name:
                            try:
                                index = self._communication_session_xqueries_list.index(
                                    field_name
                                )
                                if index < len(view[obj_id]):
                                    view[obj_id][index] = e.value
                            except (ValueError, IndexError):
                                pass
        elif idx == getattr(self, "users_view_idx", None):
            view = self.tables[idx][0]
            if hasattr(object, "values"):
                for e in object.values:
                    if hasattr(e, "value") and hasattr(e, "field_index"):
                        field_name = self.xqueries_tables.get("users", {}).get(
                            e.field_index
                        )
                        if field_name:
                            try:
                                index = self._user_xqueries_list.index(field_name)
                                if index < len(view[obj_id]):
                                    view[obj_id][index] = e.value
                            except (ValueError, IndexError):
                                pass
        elif idx == getattr(self, "queues_view_idx", None):
            view = self.tables[idx][0]
            if hasattr(object, "values"):
                for e in object.values:
                    if hasattr(e, "value") and hasattr(e, "field_index"):
                        field_name = self.xqueries_tables.get("queues", {}).get(
                            e.field_index
                        )
                        if field_name:
                            try:
                                index = self._service_xqueries_list.index(field_name)
                                if index < len(view[obj_id]):
                                    view[obj_id][index] = e.value
                            except (ValueError, IndexError):
                                pass
        elif idx in self.tables:
            view = self.tables[idx][0]
            if obj_id not in view:
                view[obj_id] = []
            if hasattr(object, "values"):
                for e in object.values:
                    if hasattr(e, "value"):
                        view[obj_id].append(e.value)

    def query_list(self, idx, db_root, filter):
        self.protocol.sendMessage(
            message.query_list, 1, idx, self.db_path, 0, db_root, filter, 0, "", 0
        )

    def query_object(self, idx, id, format_id, obj_id):
        self.protocol.sendMessage(
            message.query_object, 1, idx, self.db_path, id, format_id, obj_id
        )

    def on_connection_ok(self, server_version, server_date):
        print(f"  -> Connexion OK: version={server_version}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("  -> Login OK")
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print(f"  -> ERREUR login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("  -> Index OK")
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()

        self.sessions_view_idx = self.start_view(
            "sessions",
            "communications_sessions",
            self._communication_session_xqueries_list,
            "",
        )
        print(f"  -> Vue sessions creee: {self.sessions_view_idx}")

        self.users_view_idx = self.start_view(
            "users",
            "users",
            self._user_xqueries_list,
            "",
        )
        print(f"  -> Vue users creee: {self.users_view_idx}")

        self.queues_view_idx = self.start_view(
            "queues",
            "queues",
            self._service_xqueries_list,
            "",
        )
        print(f"  -> Vue queues creee: {self.queues_view_idx}")

        print("  -> Attente de 3 secondes pour les donnees...")
        reactor.callLater(3, self.extract_data)

    def extract_data(self):
        print(f"\n{'=' * 60}")
        print(f"=== PROJET: {self.project} - {self.db_path} ===")
        print(f"{'=' * 60}")

        all_sessions = []
        all_users = []
        all_queues = []
        max_retries = 10
        retry_count = [0]

        def poll_for_data():
            retry_count[0] += 1

            sessions_ready = (
                hasattr(self, "sessions_view_idx")
                and self.sessions_view_idx
                and self.tables.get(self.sessions_view_idx)
            )
            users_ready = (
                hasattr(self, "users_view_idx")
                and self.users_view_idx
                and self.tables.get(self.users_view_idx)
            )
            queues_ready = (
                hasattr(self, "queues_view_idx")
                and self.queues_view_idx
                and self.tables.get(self.queues_view_idx)
            )

            if sessions_ready:
                view = self.tables[self.sessions_view_idx][0]
                count = len(view)
                print(f"  -> Sessions: {count} entrees")

            if users_ready:
                users_view = self.tables[self.users_view_idx][0]
                users_count = len(users_view)
                print(f"  -> Users: {users_count} entrees")

            if queues_ready:
                queues_view = self.tables[self.queues_view_idx][0]
                queues_count = len(queues_view)
                print(f"  -> Queues: {queues_count} entrees")

            if (
                sessions_ready
                and users_ready
                and queues_ready
                and users_count > 0
                and queues_count > 0
            ):
                print(
                    f"Donnees recues: sessions={count}, users={users_count}, queues={queues_count}"
                )

                for obj_id, data in view.items():
                    if data and isinstance(data, list):
                        data_dict = dict(
                            zip(self._communication_session_xqueries_list, data)
                        )
                        session_id = str(data_dict.get("session_id", ""))
                        if session_id.startswith("b'"):
                            session_id = session_id[2:-1]
                        all_sessions.append(
                            {
                                "id": obj_id,
                                "create_date": str(data_dict.get("create_date", "")),
                                "session_type": format_session_type(
                                    data_dict.get("session_type", "")
                                ),
                                "session_id": session_id,
                                "terminate_date": str(
                                    data_dict.get("terminate_date", "")
                                ),
                                "user_login": str(data_dict.get("user.login", "")),
                                "user_name": str(data_dict.get("user.name", "")),
                            }
                        )

                for obj_id, data in users_view.items():
                    if data and isinstance(data, list):
                        data_dict = dict(zip(self._user_xqueries_list, data))
                        all_users.append(data_dict)

                for obj_id, data in queues_view.items():
                    if data and isinstance(data, list):
                        data_dict = dict(zip(self._service_xqueries_list, data))
                        name = clean_string(data_dict.get("name", ""))
                        display_name = clean_string(data_dict.get("display_name", ""))

                        if not name or name.startswith("VQ_") or "@cdep://" in name:
                            continue

                        all_queues.append(
                            {
                                "id": str(obj_id),
                                "name": name,
                                "display_name": display_name,
                                "logged": int(
                                    data_dict.get("logged_sessions_count", 0) or 0
                                ),
                                "working": int(
                                    data_dict.get("working_sessions_count", 0) or 0
                                ),
                                "waiting": int(
                                    data_dict.get("waiting_tasks_count", 0) or 0
                                ),
                            }
                        )

                process_results()
            elif retry_count[0] < max_retries:
                print(f"Attente donnees... (tentative {retry_count[0]}/{max_retries})")
                reactor.callLater(2, poll_for_data)
            else:
                print("Aucune donnee recue apres toutes les tentatives")
                process_results()

        def process_results():
            active = [
                s
                for s in all_sessions
                if not s.get("terminate_date")
                or s.get("terminate_date") in ("", "None")
            ]
            terminated = [
                s
                for s in all_sessions
                if s.get("terminate_date")
                and s.get("terminate_date") not in ("", "None")
            ]

            calls_incoming = []
            calls_outgoing = []
            agents = []
            seen_calls = set()

            for s in active:
                session_id = clean_string(s.get("session_id", ""))
                user_login = clean_string(s.get("user.login", ""))
                if is_call_session(session_id):
                    if session_id in seen_calls:
                        continue
                    seen_calls.add(session_id)
                    if s.get("session_type") == "incoming":
                        calls_incoming.append(
                            {
                                "session_id": session_id,
                                "caller": user_login if user_login else "En_attente",
                                "callee": "",
                                "start_time": format_date_to_second(
                                    s.get("create_date", "")
                                ),
                                "status": "active",
                            }
                        )
                    else:
                        calls_outgoing.append(
                            {
                                "session_id": session_id,
                                "caller": user_login if user_login else "En_attente",
                                "callee": "",
                                "start_time": format_date_to_second(
                                    s.get("create_date", "")
                                ),
                                "status": "active",
                            }
                        )
                elif is_agent_session(session_id):
                    agents.append(
                        {
                            "login": user_login,
                            "name": clean_string(s.get("user.name", "")),
                            "session_id": session_id,
                        }
                    )

            terminated_calls = []
            seen_terminated = set()
            for s in terminated:
                session_id = clean_string(s.get("session_id", ""))
                if is_call_session(session_id):
                    if session_id in seen_terminated:
                        continue
                    seen_terminated.add(session_id)
                    terminated_calls.append(
                        {
                            "session_id": session_id,
                            "type": s.get("session_type", ""),
                            "start_time": format_date_to_second(
                                s.get("create_date", "")
                            ),
                            "end_time": format_date_to_second(
                                s.get("terminate_date", "")
                            ),
                            "user": clean_string(s.get("user.login", "")),
                        }
                    )

            terminated_calls.sort(key=lambda x: x.get("end_time", ""), reverse=True)

            users_from_dispatch = []
            user_sessions_set = set()
            user_session_map = {}

            for s in all_sessions:
                user_login = clean_string(s.get("user.login", ""))
                sess_id = clean_string(s.get("session_id", ""))
                if (
                    user_login
                    and is_agent_session(sess_id)
                    and user_login not in user_session_map
                ):
                    user_session_map[user_login] = sess_id

            for s in all_users:
                login = clean_string(s.get("login", ""))
                name = clean_string(s.get("name", "")) or login
                state = clean_string(s.get("last_state_display_name", ""))
                last_task = clean_string(s.get("last_task_display_name", ""))
                login_date = clean_string(s.get("sessions.last.session.login_date", ""))
                session_id = clean_string(s.get("sessions.last.session.session_id", ""))
                phone = clean_string(s.get("sessions.last.session.phone_uri", ""))
                profile = clean_string(s.get("sessions.last.session.profile_name", ""))

                if not login or login in user_sessions_set:
                    continue
                user_sessions_set.add(login)

                user_type = "agent"
                if login.startswith("supervisor"):
                    user_type = "supervisor"

                login_duration_formatted = "-"
                login_duration_seconds = 0
                if login_date and login_date not in ("", "None"):
                    try:
                        login_dt = datetime.fromisoformat(
                            login_date.replace("Z", "+00:00")
                        )
                        now = datetime.now(timezone.utc if login_dt.tzinfo else None)
                        login_duration_seconds = int((now - login_dt).total_seconds())
                        if login_duration_seconds < 60:
                            login_duration_formatted = f"{login_duration_seconds}s"
                        elif login_duration_seconds < 3600:
                            login_duration_formatted = (
                                f"{login_duration_seconds // 60}m"
                            )
                        else:
                            hours = login_duration_seconds // 3600
                            minutes = (login_duration_seconds % 3600) // 60
                            login_duration_formatted = f"{hours}h{minutes}m"
                    except:
                        login_duration_formatted = "-"

                users_from_dispatch.append(
                    {
                        "id": session_id.split("@")[0].replace("user_", "") or "0",
                        "login": login,
                        "name": name,
                        "state": state or "unknown",
                        "profile": profile,
                        "phone": phone,
                        "service": "",
                        "logged_in": True,
                        "type": user_type,
                        "mode": state or "unknown",
                        "last_state_display_name": state or "unknown",
                        "last_state_name": clean_string(s.get("last_state_name", ""))
                        or "unknown",
                        "last_task_display_name": last_task or "-",
                        "last_task_name": clean_string(s.get("last_task_name", ""))
                        or "",
                        "login_date": login_date,
                        "session_id": session_id,
                        "state_start_date": clean_string(
                            s.get("states.last.state.start_date", "")
                        )
                        or "",
                        "login_duration_seconds": login_duration_seconds,
                        "login_duration_formatted": login_duration_formatted,
                    }
                )

            agents = [
                {
                    "login": u.get("login", ""),
                    "name": u.get("name", ""),
                    "session_id": u.get("session_id", ""),
                }
                for u in users_from_dispatch
            ]

            queues_from_dispatch = [
                q
                for q in all_queues
                if q.get("name", "") and not q.get("name", "").startswith("_")
            ]

            output = {
                "project": self.project,
                "db_path": self.db_path,
                "connected": True,
                "timestamp": datetime.now().isoformat(),
                "active": {
                    "incoming_calls": calls_incoming,
                    "outgoing_calls": calls_outgoing,
                    "agents": agents,
                    "total_incoming": len(calls_incoming),
                    "total_outgoing": len(calls_outgoing),
                    "total_agents": len(agents),
                },
                "terminated": {
                    "calls": terminated_calls,
                    "count": len(terminated_calls),
                },
                "users": users_from_dispatch,
                "queues": queues_from_dispatch,
            }

            print(f"\n=== RESULTATS ===")
            print(f"Appels entrants actifs: {len(calls_incoming)}")
            print(f"Appels sortants actifs: {len(calls_outgoing)}")
            print(f"Agents actifs: {len(agents)}")
            print(f"Appels termines: {len(terminated_calls)}")

            print(f"\n=== JSON ===")
            print(json.dumps(output, indent=2, default=str))

            self.output = output
            self.stop()

        reactor.callLater(3, poll_for_data)

    def stop(self):
        print("\nDeconnexion...")
        try:
            self.protocol.transport.loseConnection()
        except:
            pass
        reactor.stop()
        if self.done_callback:
            self.done_callback(self.output)


def get_dispatch_sessions(
    ip="10.199.30.67", port=20103, project="MPU_PREPROD", timeout=45
):
    import threading
    import time
    from multiprocessing import Queue

    result_queue = Queue()

    def run_client():
        client = ProjectDispatchClient("dispatch_test", ip, port, project)
        client.done_callback = lambda out: result_queue.put(out)
        client.connect()
        reactor.run()

    def stop_reactor():
        time.sleep(timeout)
        try:
            reactor.callLater(0, reactor.stop)
        except:
            pass

    thread = threading.Thread(target=run_client)
    thread.daemon = True
    thread.start()

    stop_thread = threading.Thread(target=stop_reactor)
    stop_thread.daemon = True
    stop_thread.start()

    try:
        result = result_queue.get(timeout=timeout + 2)
        return result
    except:
        return None


def recup_dispatch_project(ip="10.199.30.67", port=20103, project="MPU_PREPROD"):
    print(f"=== Test Dispatch CCCP - Projet {project} ===")
    print(f"Serveur: {ip}:{port}")
    print(f"Chemin: /dispatch_{project}")

    client = ProjectDispatchClient("dispatch_test", ip, port, project)
    client.connect()
    reactor.run()


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20103
    project = sys.argv[3] if len(sys.argv) > 3 else "MPU_PREPROD"

    recup_dispatch_project(ip, port, project)
