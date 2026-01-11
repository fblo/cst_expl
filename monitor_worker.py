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
CALL_HISTORY_FILE = "/tmp/cccp_call_history.json"
UPDATE_INTERVAL = 10
TEST_SCRIPT = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"

data = {
    "ip": DEFAULT_IP,
    "connected": False,
    "last_update": None,
    "users": [],
    "queues": [],
    "calls": {"incoming": 0, "outgoing": 0, "active": 0},
    "call_history": [],
    "stats": {"total_users": 0, "supervisors": 0, "agents": 0, "logged_in": 0},
    "errors": [],
}


# Load persisted call history
def load_call_history():
    try:
        with open(CALL_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_call_history(history):
    try:
        with open(CALL_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde historique: {e}")


def format_duration(seconds):
    """Formate une durée en secondes vers un format lisible"""
    if seconds < 0:
        return "-"
    elif seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m{secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h{minutes}m"


def calculate_durations(task):
    """Calcule les durées d'un appel à partir des dates"""
    start_date = task.get("start_date", "")
    end_date = task.get("end_date", "")
    stop_waiting_date = task.get("stop_waiting_date", "")
    management_date = task.get("management_date", "")

    waiting_duration = 0
    managing_duration = 0
    total_duration = 0

    try:
        if start_date and start_date != "None":
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

            if end_date and end_date != "None":
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                total_duration = int((end_dt - start_dt).total_seconds())

            if stop_waiting_date and stop_waiting_date != "None":
                waiting_dt = datetime.fromisoformat(
                    stop_waiting_date.replace("Z", "+00:00")
                )
                waiting_duration = int((waiting_dt - start_dt).total_seconds())

            if management_date and management_date != "None":
                manage_dt = datetime.fromisoformat(
                    management_date.replace("Z", "+00:00")
                )
                managing_duration = (
                    int(
                        (end_dt or datetime.now(timezone.utc)) - manage_dt
                    ).total_seconds()
                    if end_date
                    else 0
                )
                # Si on a la date de fin, recalculer précisément
                if end_date and end_date != "None" and management_date != "None":
                    manage_dt = datetime.fromisoformat(
                        management_date.replace("Z", "+00:00")
                    )
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    managing_duration = int((end_dt - manage_dt).total_seconds())
    except Exception as e:
        print(f"Erreur calcul durées: {e}")

    return {
        "waiting_duration": format_duration(waiting_duration),
        "managing_duration": format_duration(managing_duration),
        "total_duration": format_duration(total_duration),
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


demo_users = [
    {
        "id": 6,
        "login": "consistent",
        "name": "consistent",
        "state": "supervisor unplug",
        "profile": "Superviseur_default",
        "logged_in": True,
        "type": "supervisor",
    },
    {
        "id": 15,
        "login": "agt_mpu_preprod",
        "name": "agt_mpu_preprod",
        "state": "unplug",
        "profile": "Profile_Test",
        "logged_in": True,
        "type": "agent",
    },
    {
        "id": 100,
        "login": "fblo",
        "name": "FBLO",
        "state": "supervisor plugged",
        "profile": "Superviseur_default",
        "logged_in": True,
        "type": "supervisor",
    },
]

demo_queues = [
    {
        "id": 3,
        "name": "test_queue_vocal1",
        "display_name": "Test Queue Vocal 1",
        "logged": 0,
        "working": 0,
        "waiting": 0,
    },
    {
        "id": 4,
        "name": "queue_2",
        "display_name": "Queue 2",
        "logged": 0,
        "working": 0,
        "waiting": 0,
    },
    {
        "id": 5,
        "name": "agt_mpu_preprod",
        "display_name": "Agent MPU Preprod",
        "logged": 1,
        "working": 0,
        "waiting": 0,
    },
]


def fetch_cccp_data():
    """Recupere les donnees CCCP via subprocess"""
    try:
        result = subprocess.run(
            [sys.executable, TEST_SCRIPT, DEFAULT_IP, str(DISPATCH_PORT)],
            capture_output=True,
            text=True,
            timeout=20,
        )

        if result.returncode != 0:
            log_error(f"Script erreur: {result.stderr}")
            return None

        output = result.stdout.strip()
        if not output:
            log_error("Pas de sortie du script")
            return None

        return json.loads(output)

    except subprocess.TimeoutExpired:
        log_error("Timeout du script CCCP")
        return None
    except json.JSONDecodeError as e:
        log_error(f"JSON decode error: {e}")
        return None
    except Exception as e:
        log_error(f"Erreur subprocess: {e}")
        return None


def process_cccp_data(cccp_data):
    """Traite les donnees recues du CCCP"""
    if cccp_data is None or cccp_data.get("error"):
        return None, None, []

    users = []
    call_history = []

    # Traiter TOUS les utilisateurs en une seule passe
    cccp_users = cccp_data.get("users", [])
    print(f"DEBUG: Processing {len(cccp_users)} CCCP users")

    for u in cccp_users:
        login = u.get("login", "")
        profile = u.get("sessions.last.session.profile_name", "")
        logged_str = u.get("sessions.last.session.logged", "False")
        logged = str(logged_str).lower() == "true"

        print(f"DEBUG: {login} - logged={logged_str} -> {logged}")

        # Garder tous les utilisateurs connectés
        if not logged:
            print(f"DEBUG: Skipping {login} - not logged")
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

        if profile == "Superviseur_default":
            user_type = "supervisor"
            if "interface" in mode.lower():
                state = "supervisor interface"
            else:
                state = "supervisor plugged"
        else:
            last_state = u.get("last_state_name", "").lower()

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

        # Calculer la durée de connexion
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

        print(f"DEBUG: Adding {login} ({user_type}) to users list")

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

    print(f"DEBUG: Returning {len(users)} users from process_cccp_data")

    # Load persisted call history
    persisted_history = load_call_history()
    existing_task_ids = {call.get("task_id") for call in persisted_history}

    # Process new calls from CCCP
    new_calls = []
    for call in cccp_data.get("call_history", []):
        task_id = call.get("task_id", "")

        # Only process new calls (not in persisted history)
        if task_id and task_id not in existing_task_ids:
            # Get pre-calculated durations from the dispatch data
            waiting_duration = call.get("waiting_duration", "0s")
            managing_duration = call.get("managing_duration", "0s")
            post_mgmt_duration = call.get("post_management_duration", "0s")
            total_duration = call.get("total_duration", "0s")

            # Parse start date for formatting with LOCAL timezone
            start_date_utc = call.get("start_date", "")
            start_date_local = ""
            start_time_local = ""

            if start_date_utc and start_date_utc != "None":
                try:
                    # Parse as UTC
                    if start_date_utc.endswith("Z"):
                        start_date_utc = start_date_utc[:-1] + "+00:00"
                    dt_utc = datetime.fromisoformat(start_date_utc)

                    # Convert to local timezone
                    from datetime import timezone

                    dt_local = dt_utc.astimezone()

                    start_date_local = dt_local.strftime("%d/%m/%Y")
                    start_time_local = dt_local.strftime("%H:%M:%S")
                except Exception as e:
                    print(f"DEBUG: Error parsing date {start_date_utc}: {e}")
                    # Fallback to just extracting time from string
                    if "T" in start_date_utc:
                        start_time_local = (
                            start_date_utc.split("T")[1].split("+")[0].split("Z")[0]
                        )

            new_calls.append(
                {
                    "task_id": task_id,
                    "queue_type": call.get("queue_type", ""),
                    "queue_display_name": call.get("queue_display_name", ""),
                    "start_date_utc": start_date_utc,
                    "start_date": start_date_local,
                    "start_time": start_time_local,
                    "waiting_duration": waiting_duration,
                    "managing_duration": managing_duration,
                    "post_management_duration": post_mgmt_duration,
                    "total_duration": total_duration,
                    "manager_login": call.get("manager_login", ""),
                    "manager_profile": call.get("manager_profile", ""),
                    "caller": call.get("caller", ""),
                    "callee": call.get("callee", ""),
                }
            )

    # Add new calls to persisted history
    call_history = new_calls + persisted_history

    # Keep only last 500 calls
    call_history = call_history[:500]

    # Save updated history
    save_call_history(call_history)

    # Format call history for display (last 100)
    display_history = []
    for call in call_history[:100]:
        # Use pre-formatted local dates
        date_str = call.get("start_date", "")
        time_str = call.get("start_time", "")

        display_history.append(
            {
                "task_id": call.get("task_id", ""),
                "queue_type": call.get("queue_type", ""),
                "queue_display_name": call.get("queue_display_name", ""),
                "start_date": date_str,
                "start_time": time_str,
                "waiting_duration": call.get("waiting_duration", ""),
                "managing_duration": call.get("managing_duration", ""),
                "post_management_duration": call.get("post_management_duration", ""),
                "total_duration": call.get("total_duration", ""),
                "manager_login": call.get("manager_login", ""),
                "manager_profile": call.get("manager_profile", ""),
                "caller": call.get("caller", ""),
                "callee": call.get("callee", ""),
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

    return users, queues, call_history


def monitoring_loop():
    cycle = 0
    last_connected = False

    while True:
        cycle += 1

        try:
            cccp_data = fetch_cccp_data()
            users, queues, call_history = process_cccp_data(cccp_data)

            if users is None:
                data["connected"] = False
                data["users"] = demo_users.copy()
                data["queues"] = demo_queues.copy()
            else:
                data["connected"] = True
                data["users"] = users
                data["queues"] = queues
                data["call_history"] = call_history

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
                    f"  Utilisateurs: {len(data['users'])}, Queues: {len(data['queues'])}, Appels: {len(data['call_history'])}"
                )

        except Exception as e:
            log_error(f"Erreur: {e}")

        time.sleep(UPDATE_INTERVAL)


def init_data():
    data["users"] = demo_users.copy()
    data["queues"] = demo_queues.copy()
    data["call_history"] = []
    data["events"] = []
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
