#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from datetime import datetime

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
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str


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
        self.all_sessions = []
        self.done_callback = None

    def on_list_response(self, session_id, idx, object):
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
                                index = [
                                    "create_date",
                                    "session_type",
                                    "session_id",
                                    "terminate_date",
                                    "user.login",
                                    "user.name",
                                ].index(field_name)
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
            [
                "create_date",
                "session_type",
                "session_id",
                "terminate_date",
                "user.login",
                "user.name",
            ],
            "",
        )
        print(f"  -> Vue sessions creee: {self.sessions_view_idx}")
        print("  -> Attente de 5 secondes pour les donnees...")
        reactor.callLater(5, self.extract_data)

    def extract_data(self):
        print(f"\n{'=' * 60}")
        print(f"=== PROJET: {self.project} - {self.db_path} ===")
        print(f"{'=' * 60}")

        all_sessions = []
        max_retries = 8
        retry_count = [0]

        def poll_for_data():
            retry_count[0] += 1

            if (
                hasattr(self, "sessions_view_idx")
                and self.sessions_view_idx
                and self.tables.get(self.sessions_view_idx)
            ):
                view = self.tables[self.sessions_view_idx][0]
                count = len(view)

                if count > 0:
                    print(f"Donnees recues: {count} entrees")
                    for obj_id, data in view.items():
                        if data and isinstance(data, list):
                            session_id = str(data[2]) if len(data) > 2 else ""
                            if session_id.startswith("b'"):
                                session_id = session_id[2:-1]
                            all_sessions.append(
                                {
                                    "id": obj_id,
                                    "create_date": str(data[0])
                                    if len(data) > 0
                                    else "",
                                    "session_type": format_session_type(data[1]),
                                    "session_id": session_id,
                                    "terminate_date": str(data[3])
                                    if len(data) > 3
                                    else "",
                                    "user_login": str(data[4]) if len(data) > 4 else "",
                                    "user_name": str(data[5]) if len(data) > 5 else "",
                                }
                            )
                    process_results()
                elif retry_count[0] < max_retries:
                    print(
                        f"Attente donnees... (tentative {retry_count[0]}/{max_retries})"
                    )
                    reactor.callLater(2, poll_for_data)
                else:
                    print("Aucune donnee recue apres toutes les tentatives")
                    process_results()
            elif retry_count[0] < max_retries:
                print(f"Attente donnees... (tentative {retry_count[0]}/{max_retries})")
                reactor.callLater(2, poll_for_data)
            else:
                print("Aucune donnee recue")
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
                session_id = s.get("session_id", "")
                user_login = (
                    s.get("user_login", "").strip("b'").strip("'").strip('"').strip('"')
                    if s.get("user_login")
                    else ""
                )
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
                            "login": s.get("user_login", "").strip("b'").strip("'"),
                            "name": s.get("user_name", "").strip("b'").strip("'"),
                            "session_id": session_id,
                        }
                    )

            terminated_calls = []
            seen_terminated = set()
            for s in terminated:
                session_id = s.get("session_id", "")
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
                            "user": s.get("user_login", "").strip("b'").strip("'")
                            if s.get("user_login")
                            else "",
                        }
                    )

            terminated_calls.sort(key=lambda x: x.get("end_time", ""), reverse=True)

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
    ip="10.199.30.67", port=20103, project="MPU_PREPROD", timeout=25
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


def test_dispatch_project(ip="10.199.30.67", port=20103, project="MPU_PREPROD"):
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

    test_dispatch_project(ip, port, project)
