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
from cccp.protocols.rt.lookup import IndicatorLuT
from cccp.protocols.rt.subscriber import Subscriber
from cccp.protocols.rt.indicators import (
    CallId,
    CallStartDate,
    CallEndDate,
    LocalNumber,
    RemoteNumber,
    SessionId,
    SessionTerminateDate,
    TaskStartDate,
    TaskManagedStartDate,
)


class IV2USMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(IV2USMonitor, self).__init__(name, ip, port)
        self.cycle_count = 0
        self.subscriber = None
        self.indicator_lut = IndicatorLuT()

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur IV2US {self.ip}:{self.port}")
        print(f"Version serveur: {server_version}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print(f"✅ Login OK - Session ID: {session_id}")
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("🔧 Index par défaut initialisé")
        # Créer un subscriber et configurer pour les communications
        reactor.callLater(1, self.setup_communications)

    def setup_communications(self):
        """Configure le subscriber pour les communications IV2US"""
        try:
            print("📞 Configuration du subscriber IV2US...")

            # Ajouter les indicateurs de communication
            self.indicator_lut.add_indicator(CallId())
            self.indicator_lut.add_indicator(CallStartDate())
            self.indicator_lut.add_indicator(CallEndDate())
            self.indicator_lut.add_indicator(LocalNumber())
            self.indicator_lut.add_indicator(RemoteNumber())
            # SessionType n'existe pas, on l'omet
            self.indicator_lut.add_indicator(SessionId())
            self.indicator_lut.add_indicator(SessionTerminateDate())
            self.indicator_lut.add_indicator(TaskStartDate())
            self.indicator_lut.add_indicator(TaskManagedStartDate())

            print("✅ Indicateurs configurés")

            # Créer le subscriber pour les communications
            self.subscriber = Subscriber(self.indicator_lut)

            print("📞 Création subscription...")
            result = self.subscriber.subscribe_communication(
                target="all",
                indicators_list=[
                    "communication_id",
                    "session_type",
                    "session_id",
                    "terminate_date",
                    "user_login",
                    "manager_session.user.login",
                    "queue_name",
                    "attributes.local_number.value",
                    "attributes.remote_number.value",
                    "start_date",
                    "management_effective_date",
                    "create_date",
                    "last_record.value",
                    "record_active.value",
                    "last_state_display_name",
                    "last_task_display_name",
                    "connections/last/call_id",
                    "last_state_start_date",
                ],
                profiles_list=[],  # Tous les profils
                queues_list=[],  # Toutes les queues
            )

            print(f"✅ Subscription ID: {result.get('id', 'unknown')}")

            # Démarrer le monitoring
            reactor.callLater(2, self.start_monitoring)

        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
            import traceback

            traceback.print_exc()
            self.stop()

    def start_monitoring(self):
        print("📞 Démarrage monitoring des appels IV2US...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 60}")
        print(f"📞 CYCLE {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        try:
            # Récupérer les communications actives depuis le listener
            if hasattr(self.indicator_lut, "get_communication_listener"):
                listener = self.indicator_lut.get_communication_listener()
                if listener:
                    try:
                        communications = listener.get_values(
                            [
                                "communication_id",
                                "session_type",
                                "session_id",
                                "terminate_date",
                                "user_login",
                                "manager_session.user.login",
                                "queue_name",
                                "attributes.local_number.value",
                                "attributes.remote_number.value",
                                "start_date",
                                "management_effective_date",
                                "create_date",
                                "last_record.value",
                                "record_active.value",
                                "last_state_display_name",
                                "last_state_display_name",
                                "connections/last/call_id",
                                "last_state_start_date",
                            ]
                        )

                        self.display_communications(communications)

                    except Exception as e:
                        print(f"❌ Erreur récupération: {e}")
                        import traceback

                        traceback.print_exc()
                else:
                    print("❌ CommunicationListener non disponible")
            else:
                print("❌ CommunicationListener non disponible")

        except Exception as e:
            print(f"❌ Erreur monitoring: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring
        reactor.callLater(5, self.monitor_loop)

    def display_communications(self, communications):
        """Affiche les communications trouvées"""
        if not communications or len(communications) == 0:
            print("   📭 Aucune communication active")
            return

        print(f"📊 {len(communications)} communication(s) trouvée(s):")
        print()

        for i, comm in enumerate(communications, 1):
            comm_id = comm.get("communication_id", "N/A")
            session_type = comm.get("session_type", "N/A")
            session_id = comm.get("session_id", "N/A")
            terminate_date = comm.get("terminate_date", "")

            user_login = comm.get("user_login") or comm.get(
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

            status = (
                "🟢 ACTIF"
                if not terminate_date or terminate_date in ("", "None")
                else "🔴 TERMINÉ"
            )

            print(f"📞 {i}. {status} - {user_login}")
            print(f"   📋 Communication ID: {comm_id}")
            print(f"   🆔 Session ID: {session_id}")
            print(f"   📊 Type: {session_type}")
            print(f"   📱 Local: {local_number or 'N/A'}")
            print(f"   📝 Remote: {remote_number or 'N/A'}")
            print(f"   🏷️ File: {queue_name}")
            print(f"   ⏰️ Début: {start_date or create_date}")
            print(f"   🕐 Création: {create_date}")

            # Ajouter l'état détaillé
            last_state = comm.get("last_state_display_name", "N/A")
            start_state_date = comm.get("last_state_start_date", "")
            call_id = comm.get("connections/last/call_id", "")

            if last_state:
                print(f"   📞 État: {last_state}")
            if start_state_date:
                print(f"   ⏰️ Début état: {start_state_date}")
            if call_id:
                print(f"   📞 Call ID: {call_id}")

            print()

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Démarrage du monitoring IV2US...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Monitoring direct avec IndicatorLuT pour IV2US")
    print("Press Ctrl+C pour arrêter\n")

    client = IV2USMonitor("iv2us_monitor", DEFAULT_IP, DEFAULT_PORT)

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
