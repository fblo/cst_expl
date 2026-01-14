#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script simple pour afficher les appels inbound/outbound en direct depuis le CCCP

import sys
import json
import time
import subprocess
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

DEFAULT_IP = "10.199.30.67"
DISPATCH_PORT = 20103
TEST_SCRIPT = "/home/fblo/Documents/repos/iv-cccp/test_dispatch_json.py"


def fetch_cccp_data():
    """Récupère les données depuis le script de test"""
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
            print(f"❌ Erreur script CCCP: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout du script CCCP")
        return None
    except Exception as e:
        print(f"❌ Erreur de récupération: {e}")
        return None


def display_calls(cccp_data):
    """Affiche les appels en cours"""

    print("\n" + "=" * 60)
    print(f"📞 APPELS EN COURS - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    if not cccp_data:
        print("❌ Pas de données CCCP")
        return

    inbound_calls = cccp_data.get("calls_inbound", [])
    outbound_calls = cccp_data.get("calls_outbound", [])
    history_calls = cccp_data.get("calls_history", [])

    print(f"📥 Appels entrants: {len(inbound_calls)}")
    for i, call in enumerate(inbound_calls, 1):
        session_id = call.get("session_id", call.get("id", ""))
        user_login = call.get("user.login", call.get("manager_session.user.login", ""))
        local_number = call.get("attributes.local_number.value", "")
        remote_number = call.get("attributes.remote_number.value", "")
        create_date = call.get("create_date", "")
        start_date = call.get("start_date", "")
        terminate_date = call.get("terminate_date", "")

        if local_number and local_number.startswith("tel:"):
            local_number = local_number[4:]
        if remote_number and remote_number.startswith("tel:"):
            remote_number = remote_number[4:]

        print(f"  📞 {i}. {user_login or 'N/A'}")
        print(f"     ID: {session_id}")
        print(f"     Appelant: {remote_number or 'N/A'}")
        print(f"     Agent: {local_number or 'N/A'}")
        print(f"     Début: {start_date or create_date or 'N/A'}")
        if terminate_date and terminate_date not in ("", "None"):
            print(f"     Fin: {terminate_date}")
        print()

    print(f"📤 Appels sortants: {len(outbound_calls)}")
    for i, call in enumerate(outbound_calls, 1):
        session_id = call.get("session_id", call.get("outbound_call_id.value", ""))
        user_login = call.get("user.login", "")
        user_name = call.get("user.name", "")
        target = call.get("last_outbound_call_target.value", "")
        start_date = call.get("last_outbound_call_contact_start.value", "")
        terminate_date = call.get("terminate_date", "")

        print(f"  📞 {i}. {user_login or user_name or 'N/A'}")
        print(f"     ID: {session_id}")
        print(f"     Cible: {target or 'N/A'}")
        print(f"     Début: {start_date or 'N/A'}")
        if terminate_date and terminate_date not in ("", "None"):
            print(f"     Fin: {terminate_date}")
        print()

    if not inbound_calls and not outbound_calls:
        print("   Aucun appel actif")

    print("=" * 60)
    print(f"📊 Historique récent: {len(history_calls)} appels")
    if history_calls:
        print("   (Derniers appels terminés aujourd'hui)")

    total_active = len(inbound_calls) + len(outbound_calls)
    return total_active > 0


def main():
    print("🚀 Démarrage du monitoring d'appels CCCP...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DISPATCH_PORT}")
    print("⚡ Actualisation toutes les 5 secondes")
    print("Press Ctrl+C pour arrêter\n")

    try:
        cycle = 0
        while True:
            cycle += 1

            # Effacer l'écran (sauf la première fois)
            if cycle > 1:
                print("\033[2J\033[H")
                print(f"🚀 Monitoring CCCP - Cycle {cycle}")
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')}\n")

            cccp_data = fetch_cccp_data()
            has_calls = display_calls(cccp_data)

            if not has_calls:
                print("😴 En attente d'appels...")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du monitoring")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
