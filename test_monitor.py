#!/usr/bin/env python3
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
    print("Fetching CCCP data...")
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, TEST_SCRIPT, DEFAULT_IP, str(DISPATCH_PORT)],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            print(f"Script erreur: {result.stderr}")
            return None

        data = json.loads(result.stdout.strip())
        print(f"CCCP returned {len(data.get('users', []))} users")
        return data
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
            print(f"  FILTERED: {login}")
            continue

        if not logged:
            print(f"  NOT LOGGED: {login}")
            continue

        user_type = "agent"
        if profile == "Superviseur_default":
            user_type = "supervisor"

        print(f"  KEEP: {login} ({user_type})")
        users.append({"login": login, "type": user_type})

    print(f"Processed {len(users)} users total")
    return users


def main():
    print("Testing monitor...")

    # Cycle unique pour tester
    print("=== Test 1: Fetching ===")
    cccp_data = get_simple_cccp_data()

    if cccp_data:
        print("=== Test 2: Processing ===")
        users = process_users(cccp_data.get("users", []))

        print(f"=== Final result: {len(users)} users ===")
        for u in users:
            print(f"  {u['login']} ({u['type']})")
    else:
        print("No data from CCCP")


if __name__ == "__main__":
    main()
