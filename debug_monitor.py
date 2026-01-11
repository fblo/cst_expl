#!/usr/bin/env python3
import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

import subprocess
import json

# Test direct
result = subprocess.run(
    [
        sys.executable,
        "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py",
        "10.199.30.67",
        "20103",
    ],
    capture_output=True,
    text=True,
    timeout=20,
)

print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout[:200]}...")
print(f"Stderr: {result.stderr[:200]}...")

if result.returncode == 0:
    cccp_data = json.loads(result.stdout.strip())
    print(f"\nNombre d'utilisateurs dans JSON: {len(cccp_data.get('users', []))}")

    users = []
    for u in cccp_data.get("users", []):
        login = u.get("login", "")
        profile = u.get("sessions.last.session.profile_name", "")
        logged_str = u.get("sessions.last.session.logged", "False")
        logged = str(logged_str).lower() == "true"

        print(f"{login}: logged={logged_str} -> {logged}")

        if not logged:
            continue

        users.append({"login": login, "profile": profile, "logged": logged})

    print(f"\nUtilisateurs après filtrage: {len(users)}")
    for u in users:
        print(f"  {u['login']}: {u['profile']}")
