#!/usr/bin/env python3
import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

import subprocess
import json

result = subprocess.run(
    [
        sys.executable,
        "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py",
        "10.199.30.67",
        "20103",
    ],
    capture_output=True,
    text=True,
    timeout=10,
)

cccp_data = json.loads(result.stdout.strip())
print(f"Total CCCP users: {len(cccp_data.get('users', []))}")

for u in cccp_data.get("users", []):
    login = u.get("login", "")
    profile = u.get("sessions.last.session.profile_name", "")
    logged_str = u.get("sessions.last.session.logged", "False")
    logged = str(logged_str).lower() == "true"

    if login == "consistent":
        print(f"  SKIP {login} (filtered)")
    elif not logged:
        print(f"  SKIP {login} (not logged: {logged_str})")
    else:
        user_type = "agent"
        if profile == "Superviseur_default":
            user_type = "supervisor"
        print(f"  KEEP {login} ({user_type}) - profile={profile}")
