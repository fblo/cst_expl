#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import subprocess

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103
TEST_SCRIPT = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"


def main():
    print("Test des appels CCCP...")

    try:
        result = subprocess.run(
            [sys.executable, TEST_SCRIPT, DEFAULT_IP, str(DISPATCH_PORT)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)

            print(f"Utilisateurs: {len(data.get('users', []))}")
            print(f"Queues: {len(data.get('queues', []))}")
            print(f"Calls inbound: {len(data.get('calls_inbound', []))}")
            print(f"Calls outbound: {len(data.get('calls_outbound', []))}")
            print(f"Calls history: {len(data.get('calls_history', []))}")

            # Afficher détails des appels
            if data.get("calls_inbound"):
                print("\n=== APPELS ENTRANTS ===")
                for i, call in enumerate(data["calls_inbound"][:5], 1):
                    print(f"{i}. Session ID: {call.get('session_id')}")
                    print(f"   User: {call.get('user.login', 'N/A')}")
                    print(
                        f"   Local: {call.get('attributes.local_number.value', 'N/A')}"
                    )
                    print(
                        f"   Remote: {call.get('attributes.remote_number.value', 'N/A')}"
                    )
                    print(f"   Start: {call.get('start_date', 'N/A')}")
                    print(f"   End: {call.get('terminate_date', 'N/A')}")
                    print()

            if data.get("calls_outbound"):
                print("=== APPELS SORTANTS ===")
                for i, call in enumerate(data["calls_outbound"][:5], 1):
                    print(f"{i}. User: {call.get('user.login', 'N/A')}")
                    print(
                        f"   Target: {call.get('last_outbound_call_target.value', 'N/A')}"
                    )
                    print(
                        f"   Start: {call.get('last_outbound_call_contact_start.value', 'N/A')}"
                    )
                    print(f"   End: {call.get('terminate_date', 'N/A')}")
                    print()
        else:
            print(f"Erreur: {result.stderr}")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    main()
