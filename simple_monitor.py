#!/usr/bin/env python3
# Version simplifiée du monitor worker

import sys
import json
import time
from datetime import datetime, timezone

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103
DATA_FILE = "/tmp/cccp_monitoring.json"
TEST_SCRIPT = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"


def get_simple_cccp_data():
    """Récupère les données du script JSON"""
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, TEST_SCRIPT, DEFAULT_IP, str(DISPATCH_PORT)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            print(f"Script erreur: {result.stderr}")
            return None

        return json.loads(result.stdout.strip())
    except Exception as e:
        print(f"Erreur: {e}")
        return None


def process_users(cccp_users):
    """Traite les utilisateurs"""
    users = []

    for u in cccp_users:
        login = u.get("login", "")
        if not login:
            continue

        profile = u.get("sessions.last.session.profile_name", "")
        logged_str = u.get("sessions.last.session.logged", "False")
        logged = str(logged_str).lower() == "true"

        if login == "consistent":
            print(f"SKIP {login} (filtered)")
            continue

        if not logged:
            print(f"SKIP {login} (not logged)")
            continue

        phone = u.get("sessions.last.session.phone_uri", "")
        mode = u.get("sessions.last.session.current_mode", "")
        login_date = u.get("sessions.last.session.login_date", "")

        if phone and phone.startswith("tel:"):
            phone = phone[4:]

        # Type d'utilisateur
        user_type = "agent"
        if profile == "Superviseur_default":
            user_type = "supervisor"

        # État
        state = "plugged"
        if profile == "Superviseur_default":
            if "interface" in mode.lower():
                state = "supervisor interface"
            else:
                state = "supervisor plugged"
        else:
            last_state = u.get("last_state_name", "").lower()
            if "sortant" in last_state:
                state = "outbound"
            elif "ringing" in last_state:
                state = "ringing"
            elif "contact" in last_state or "busy" in last_state:
                state = "busy"

        # Durée de connexion
        login_duration_seconds = 0
        if login_date and login_date != "None":
            try:
                login_dt = datetime.fromisoformat(
                    login_date.replace("+00:00", "+00:00")
                )
                now = datetime.now(timezone.utc)
                login_duration_seconds = int((now - login_dt).total_seconds())
            except:
                pass

        # Formater la durée
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

        print(f"KEEP {login} ({user_type}) - {state} - {login_duration_formatted}")
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
                "login_date": login_date,
                "session_id": u.get("sessions.last.session.session_id", ""),
                "login_duration_seconds": login_duration_seconds,
                "login_duration_formatted": login_duration_formatted,
            }
        )

    return users


def main():
    print("Starting simple monitor...")

    while True:
        try:
            print("=== Fetching CCCP data ===")
            cccp_data = get_simple_cccp_data()

            if cccp_data:
                print(f"=== CCCP returned {len(cccp_data.get('users', []))} users ===")
                users = process_users(cccp_data.get("users", []))
                queues = cccp_data.get("queues", [])

                # Filtrer les queues (pas de cdep:)
                filtered_queues = []
                for q in queues:
                    name = q.get("name", "")
                    if "cdep:" not in name.lower():
                        filtered_queues.append(
                            {
                                "id": q.get("id"),
                                "name": name,
                                "display_name": q.get("display_name", name),
                                "logged": int(q.get("logged_sessions_count", 0)),
                                "working": int(q.get("working_sessions_count", 0)),
                                "waiting": int(q.get("waiting_tasks_count", 0)),
                            }
                        )

                # Stats
                supervisors = [u for u in users if u.get("type") == "supervisor"]
                agents = [u for u in users if u.get("type") == "agent"]

                # Données complètes
                data = {
                    "connected": True,
                    "last_update": datetime.now().isoformat(),
                    "users": users,
                    "queues": filtered_queues,
                    "stats": {
                        "total_users": len(users),
                        "supervisors": len(supervisors),
                        "agents": len(agents),
                        "logged_in": len(users),
                    },
                    "events": [],
                }

                # Écrire le fichier
                print(f"=== Writing {len(users)} users to {DATA_FILE} ===")
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=2)

                print(
                    f"=== Updated: {len(users)} users, {len(filtered_queues)} queues ==="
                )
                print(f"=== Supervisors: {len(supervisors)}, Agents: {len(agents)} ===")

                # Afficher quelques utilisateurs
                for u in users[:3]:
                    print(
                        f"  {u['name']} ({u['type']}): {u['state']} - {u['login_duration_formatted']}"
                    )
            else:
                print("=== No data from CCCP ===")

        except Exception as e:
            print(f"=== Error: {e} ===")
            import traceback

            traceback.print_exc()

        print("=== Sleeping 10 seconds ===")
        time.sleep(10)  # Rafraichir toutes les 10 secondes


if __name__ == "__main__":
    main()
