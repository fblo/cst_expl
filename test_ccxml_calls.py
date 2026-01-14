#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message
from cccp.protocols.rt.subscriber import Subscriber


class CommunicationsMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(CommunicationsMonitor, self).__init__(name, ip, port)
        self.subscriber = None
        self.calls_data = []
        self.cycle_count = 0

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur CCCP {self.ip}:{self.port}")
        print(f"Version serveur: {server_version}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("🔧 Index par défaut initialisé")
        # Créer le subscriber pour les communications
        self.subscriber = Subscriber(self._indicator_lut)
        self.setup_communication_subscription()

        # Démarrer le monitoring
        reactor.callLater(2, self.start_monitoring)

    def setup_communication_subscription(self):
        try:
            print("📡 Création subscription communications...")
            # Subscribe aux communications actives
            result = self.subscriber.subscribe_communication(
                target="all",
                indicators_list=[
                    "communication_id",
                    "session_type",
                    "session_id",
                    "terminate_date",
                    "user.login",
                    "manager_session.user.login",
                    "queue_name",
                    "attributes.local_number.value",
                    "attributes.remote_number.value",
                    "start_date",
                    "management_effective_date",
                    "create_date",
                    "last_record.value",
                    "record_active.value",
                ],
                profiles_list=[],  # Tous les profils
                queues_list=[],  # Toutes les queues
            )
            print(f"📋 Subscription ID: {result.get('id', 'unknown')}")
        except Exception as e:
            print(f"❌ Erreur subscription: {e}")
            self.stop()

    def start_monitoring(self):
        print("📞 Démarrage monitoring des appels...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 60}")
        print(f"📞 CYCLE {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        # Récupérer les communications actives
        try:
            self.calls_data = self.subscriber.get_communications_values(
                "all",
                [
                    "communication_id",
                    "session_type",
                    "session_id",
                    "terminate_date",
                    "user.login",
                    "manager_session.user.login",
                    "queue_name",
                    "attributes.local_number.value",
                    "attributes.remote_number.value",
                    "start_date",
                    "management_effective_date",
                    "create_date",
                    "last_record.value",
                    "record_active.value",
                ],
            )

            self.display_calls()

        except Exception as e:
            print(f"❌ Erreur récupération communications: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring
        reactor.callLater(5, self.monitor_loop)

    def display_calls(self):
        if not self.calls_data or len(self.calls_data) == 0:
            print("   📭 Aucune communication active")
            return

        print(f"📱 {len(self.calls_data)} communication(s) active(s):")
        print()

        for i, comm in enumerate(self.calls_data, 1):
            comm_id = comm.get("communication_id", "N/A")
            session_type = comm.get("session_type", "N/A")
            session_id = comm.get("session_id", "N/A")
            terminate_date = comm.get("terminate_date", "")

            user_login = comm.get("user.login") or comm.get(
                "manager_session.user.login", "N/A"
            )

            local_number = comm.get("attributes.local_number.value") or ""
            remote_number = comm.get("attributes.remote_number.value") or ""

            if local_number and local_number.startswith("tel:"):
                local_number = local_number[4:]
            if remote_number and remote_number.startswith("tel:"):
                remote_number = remote_number[4:]

            queue_name = comm.get("queue_name", "N/A")
            start_date = comm.get("start_date") or comm.get(
                "management_effective_date", ""
            )
            create_date = comm.get("create_date", "")

            last_record = comm.get("last_record.value", "")
            record_active = comm.get("record_active.value", "")

            status = (
                "🟢 ACTIF"
                if not terminate_date or terminate_date in ("", "None")
                else "🔴 TERMINÉ"
            )

            print(f"📞 {i}. {status} - {user_login}")
            print(f"   📋 Communication ID: {comm_id}")
            print(f"   🆔 Session ID: {session_id}")
            print(f"   📞 Type: {session_type}")
            print(f"   📱 Local: {local_number or 'N/A'}")
            print(f"   📞 Remote: {remote_number or 'N/A'}")
            print(f"   🏷️ File: {queue_name}")
            print(f"   🚦 Start: {start_date}")
            print(f"   📅 Create: {create_date}")
            print(
                f"   🎥 Enregistrement: {'ON' if record_active and record_active not in ('', 'None') else 'OFF'}"
            )
            if last_record and last_record not in ("", "None"):
                print(f"   📼 Dernier enregistrement: {last_record}")
            print()

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Démarrage du monitoring CCXML des communications...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("⚡ Monitoring en temps réel des appels")
    print("Press Ctrl+C pour arrêter\n")

    client = CommunicationsMonitor("communications_monitor", DEFAULT_IP, DEFAULT_PORT)

    try:
        client.connect()
        reactor.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé")
        client.stop()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
