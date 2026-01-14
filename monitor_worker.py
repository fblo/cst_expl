#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Processus de monitoring CCCP - Donnees utilisateurs et superviseurs
# Version avec subprocess vers test_dispatch_json.py

import sys
import json
import time
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103
DATA_FILE = "/tmp/cccp_monitoring.json"
UPDATE_INTERVAL = 10
TEST_SCRIPT = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"

data = {
    "ip": DEFAULT_IP,
    "connected": False,
    "last_update": None,
    "users": [],
    "queues": [],
    "calls": {"incoming": [], "outgoing": [], "active": 0, "history": []},
    "stats": {"total_users": 0, "supervisors": 0, "agents": 0, "logged_in": 0},
    "errors": [],
}


def write_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Erreur ecriture: {e}")


def log_error(message):
    error = {"timestamp": datetime.now().isoformat(), "message": str(message)}
    data["errors"].insert(0, error)
    if len(data["errors"]) > 50:
        data["errors"] = data["errors"][:50]


def fetch_cccp_data():
    """Recupere les donnees depuis le script de test"""
    try:
        result = subprocess.run(
            [sys.executable, TEST_SCRIPT, DEFAULT_IP, str(DISPATCH_PORT)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            log_error(f"Test script error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        log_error("Test script timeout")
        return None
    except Exception as e:
        log_error(f"Erreur fetching: {e}")
        return None


def process_cccp_data(cccp_data):
    """Traite les donnees brutes du CCCP pour le dashboard"""
    users = []
    cccp_users = cccp_data.get("users", [])

    for u in cccp_users:
        login = u.get("login", "")

        # Skip utilisateur consistent
        if login == "consistent":
            continue

        profile = u.get("sessions.last.session.profile_name", "")
        logged_str = u.get("sessions.last.session.logged", "False")
        logged = str(logged_str).lower() == "true"

        # Garder tous les utilisateurs connectés
        if not logged:
            continue

        phone = u.get("sessions.last.session.phone_uri", "")
        mode = u.get("sessions.last.session.current_mode", "")
        pause_duration = u.get("state_group_pause.duration", "0")
        outbound_duration = u.get("state_group_outbound.duration", "0")
        login_date = u.get("sessions.last.session.login_date", "")
        session_id = u.get("sessions.last.session.session_id", "")
        state_start_date = u.get("states.last.state.start_date", "")

        if phone and phone.startswith("tel:"):
            phone = phone[4:]

        user_type = "agent"
        state = "plugged"

        last_state_name = u.get("last_state_name", "").lower()
        last_state_display_name = u.get("last_state_display_name", "").lower()

        if (
            (profile and "supervisor" in profile.lower())
            or login.startswith("supervisor")
            or "supervision" in last_state_name
            or "supervision" in last_state_display_name
        ):
            user_type = "supervisor"
            if "interface" in mode.lower():
                state = "supervisor interface"
            elif "unplug" in mode.lower():
                state = "supervisor unplug"
            else:
                state = "supervisor plugged"
        else:
            last_state = u.get("last_state_display_name", "").lower()

            if "sortant" in last_state or "outbound" in last_state:
                state = "outbound"
            elif "ringing" in last_state:
                state = "ringing"
            elif "contact" in last_state or "busy" in last_state:
                state = "busy"
            elif float(pause_duration) > 0:
                state = "pause"
            else:
                state = "plugged"

        login_duration_seconds = 0
        if login_date and login_date != "None" and login_date != "":
            try:
                login_dt = datetime.fromisoformat(login_date)
                now = datetime.now(timezone.utc if login_dt.tzinfo else None)
                login_duration_seconds = int((now - login_dt).total_seconds())
            except Exception as e:
                print(f"Erreur parsing date {login_date}: {e}")
                login_duration_seconds = 0

        def format_duration(seconds):
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes}m"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h{minutes}m"

        login_duration_formatted = format_duration(login_duration_seconds)

        users.append(
            {
                "id": u.get("id"),
                "login": login,
                "name": login,
                "state": state,
                "profile": profile,
                "logged_in": logged,
                "type": user_type,
                "phone": phone,
                "mode": mode,
                "last_state_display_name": u.get("last_state_display_name", ""),
                "last_state_name": u.get("last_state_name", ""),
                "last_task_display_name": u.get("last_task_display_name", ""),
                "last_task_name": u.get("last_task_name", ""),
                "login_date": login_date,
                "session_id": session_id,
                "state_start_date": state_start_date,
                "login_duration_seconds": login_duration_seconds,
                "login_duration_formatted": login_duration_formatted,
            }
        )

    queues = []
    for q in cccp_data.get("queues", []):
        name = q.get("name", "")

        if "cdep:" in name.lower():
            continue

        queues.append(
            {
                "id": q.get("id"),
                "name": name,
                "display_name": q.get("display_name", q.get("name", "")),
                "logged": int(q.get("logged_sessions_count", 0)),
                "working": int(q.get("working_sessions_count", 0)),
                "waiting": int(q.get("waiting_tasks_count", 0)),
            }
        )

    return users, queues


def process_calls_data(cccp_data, users=None, existing_history=None):
    """Traite les donnees d'appels recues du CCCP"""
    incoming_calls = []
    outgoing_calls = []
    history_calls = list(existing_history) if existing_history else []
    active_count = 0

    def calculate_duration(start_date, end_date=None):
        if not start_date or start_date in ("", "None"):
            return ""

        try:
            start_dt = datetime.fromisoformat(
                start_date.replace("/", "-").replace(" ", "T")
            )
            end_dt = (
                datetime.fromisoformat(end_date.replace("/", "-").replace(" ", "T"))
                if end_date and end_date not in ("", "None")
                else datetime.now(timezone.utc)
            )
            delta = end_dt - start_dt
            seconds = int(delta.total_seconds())
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                return f"{seconds // 60}m{seconds % 60}s"
            else:
                return f"{seconds // 3600}h{(seconds % 3600) // 60}m"
        except:
            return ""

    def format_call_data(call, call_type="inbound"):
        """Formate les donnees d'un appel"""
        terminate_date = call.get("terminate_date", "")
        local_number = call.get(
            "attributes.local_number.value", call.get("user.name", "")
        )
        remote_number = call.get(
            "attributes.remote_number.value",
            call.get("last_outbound_call_target.value", ""),
        )
        user_login = call.get("user.login", call.get("manager_session.user.login", ""))

        if local_number and local_number.startswith("tel:"):
            local_number = local_number[4:]
        if remote_number and remote_number.startswith("tel:"):
            remote_number = remote_number[4:]

        start_date = call.get(
            "start_date",
            call.get(
                "management_effective_date",
                call.get("last_outbound_call_contact_start.value", ""),
            ),
        )
        duration = calculate_duration(start_date, terminate_date)

        return {
            "id": call.get(
                "session_id", call.get("id", call.get("outbound_call_id.value", ""))
            ),
            "type": call_type,
            "local_number": local_number,
            "remote_number": remote_number,
            "user_login": user_login,
            "queue_name": call.get("queue_name", ""),
            "create_date": call.get(
                "create_date", call.get("last_outbound_call_start.value", "")
            ),
            "start_date": start_date,
            "terminate_date": terminate_date,
            "duration": duration,
        }

    # Traiter les appels entrants (communication sessions actives)
    for call in cccp_data.get("calls_inbound", []):
        terminate_date = call.get("terminate_date", "")

        if terminate_date and terminate_date not in ("", "None"):
            history_calls.append(format_call_data(call, "inbound"))
        else:
            active_count += 1
            incoming_calls.append(format_call_data(call, "inbound"))

    # Traiter les appels sortants actifs (outbound communication sessions)
    for call in cccp_data.get("calls_outbound", []):
        terminate_date = call.get("terminate_date", "")

        if terminate_date and terminate_date not in ("", "None"):
            history_calls.append(format_call_data(call, "outbound"))
        else:
            active_count += 1
            outgoing_calls.append(format_call_data(call, "outbound"))

    # Traiter les appels de l'historique (terminés aujourd'hui)
    for call in cccp_data.get("calls_history", []):
        session_type = call.get("session_type", "")
        is_outbound = str(session_type) == "3"
        call_type = "outbound" if is_outbound else "inbound"

        call_id = call.get("session_id", "")
        if not any(h["id"] == call_id for h in history_calls):
            history_calls.append(format_call_data(call, call_type))

    # Pas de fallback - on ne montre pas les états comme des appels
    # Les vrais appels doivent venir des vues CCCP

    history_calls.sort(
        key=lambda x: x.get("terminate_date", "") or x.get("create_date", ""),
        reverse=True,
    )
    history_calls = history_calls[:100]

    return {
        "incoming": incoming_calls,
        "outgoing": outgoing_calls,
        "active": active_count,
        "history": history_calls,
    }


def monitoring_loop():
    cycle = 0
    last_connected = False

    while True:
        cycle += 1

        try:
            cccp_data = fetch_cccp_data()
            users, queues = process_cccp_data(cccp_data)

            if users is None:
                data["connected"] = False
                data["users"] = []
                data["queues"] = []
                data["calls"] = {
                    "incoming": [],
                    "outgoing": [],
                    "active": 0,
                    "history": [],
                }
            else:
                data["connected"] = True
                data["users"] = users
                data["queues"] = queues

                # Traiter les donnees d'appels
                if cccp_data:
                    calls_data = process_calls_data(
                        cccp_data, users, data["calls"].get("history", [])
                    )
                    data["calls"] = calls_data
                else:
                    data["calls"] = {
                        "incoming": [],
                        "outgoing": [],
                        "active": 0,
                        "history": [],
                    }

            data["last_update"] = datetime.now().isoformat()

            supervisors = [u for u in data["users"] if u.get("type") == "supervisor"]
            agents = [u for u in data["users"] if u.get("type") == "agent"]
            logged_in = [u for u in data["users"] if u.get("logged_in")]

            data["stats"] = {
                "total_users": len(data["users"]),
                "supervisors": len(supervisors),
                "agents": len(agents),
                "logged_in": len(logged_in),
            }

            data["events"] = []

            write_data()

            connected = data["connected"]
            if connected != last_connected:
                last_connected = connected
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] {'Connecte' if connected else 'Deconnecte'} au dispatch"
                )
                print(
                    f"  Utilisateurs: {len(data['users'])}, Queues: {len(data['queues'])}"
                )

        except Exception as e:
            log_error(f"Erreur: {e}")

        time.sleep(UPDATE_INTERVAL)


def init_data():
    data["users"] = []
    data["queues"] = []
    data["events"] = []
    data["calls"] = {"incoming": [], "outgoing": [], "active": 0, "history": []}
    data["last_update"] = datetime.now().isoformat()
    write_data()
    print(
        f"Initialise: {len(data['users'])} utilisateurs, {len(data['queues'])} queues"
    )


if __name__ == "__main__":
    init_data()

    print("=" * 60)
    print("  CCCP Monitor - Utilisateurs et Superviseurs")
    print("=" * 60)
    print(f"  Fichier: {DATA_FILE}")
    print(f"  Serveur: {DEFAULT_IP}:{DISPATCH_PORT}")
    print()

    monitoring_loop()
