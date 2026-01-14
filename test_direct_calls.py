#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
from cccp.protocols.rt.lookup import IndicatorLuT
from cccp.protocols.rt.subscriber import Subscriber
import cccp.protocols.messages.explorer as message


class SimpleCallsMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(SimpleCallsMonitor, self).__init__(name, ip, port)
        self.cycle_count = 0

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur CCCP {self.ip}:{self.port}")
        print(f"Version serveur: {server_version}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print(f"✅ Login OK - Session ID: {session_id}")

        # Initialiser indicator_lut et subscriber
        self.indicator_lut = IndicatorLuT()
        self.subscriber = Subscriber(self.indicator_lut)

        # Configurer les indicateurs
        self.setup_indicators()

        self.protocol.sendMessage(message.use_default_namespaces_index)

    def setup_indicators(self):
        """Configure les indicateurs nécessaires"""
        try:
            # Ajouter les indicateurs de communication
            from cccp.protocols.rt.indicators import (
                CallId,
                CallStartDate,
                CallEndDate,
                LocalNumber,
                RemoteNumber,
                CreateDate,
                SessionType,
                SessionId,
                SessionTerminateDate,
            )

            # Ajouter les indicateurs au lookup
            self.indicator_lut.add_indicator(CallId())
            self.indicator_lut.add_indicator(CallStartDate())
            self.indicator_lut.add_indicator(CallEndDate())
            self.indicator_lut.add_indicator(LocalNumber())
            self.indicator_lut.add_indicator(RemoteNumber())
            self.indicator_lut.add_indicator(CreateDate())
            self.indicator_lut.add_indicator(SessionType())
            self.indicator_lut.add_indicator(SessionId())
            self.indicator_lut.add_indicator(SessionTerminateDate())

            print("📌 Indicateurs configurés")

        except Exception as e:
            print(f"❌ Erreur configuration indicateurs: {e}")
            import traceback

            traceback.print_exc()

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("🔧 Index par défaut initialisé")
        # Démarrer le monitoring après un petit délai
        reactor.callLater(2, self.start_monitoring)

    def start_monitoring(self):
        print("📞 Démarrage monitoring des appels...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 60}")
        print(f"📞 CYCLE {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        try:
            # Tenter de récupérer les communications depuis le listener
            if hasattr(self.indicator_lut, "get_communication_listener"):
                listener = self.indicator_lut.get_communication_listener()
                if listener:
                    communications = listener.get_values(
                        [
                            "communication_id",
                            "session_type",
                            "session_id",
                            "terminate_date",
                            "user_login",
                            "local_number",
                            "remote_number",
                            "start_date",
                            "create_date",
                        ]
                    )

                    if communications:
                        self.display_communications(communications)
                    else:
                        print("   📭 Aucune communication dans le listener")
                else:
                    print("   ❌ Pas de communication listener")
            else:
                print("   ❌ Méthode get_communication_listener non disponible")

        except Exception as e:
            print(f"❌ Erreur monitoring: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring
        reactor.callLater(3, self.monitor_loop)

    def display_communications(self, communications):
        print(f"📞 {len(communications)} communication(s) trouvée(s):")
        print()

        for i, comm in enumerate(communications, 1):
            comm_id = comm.get("communication_id", "N/A")
            session_type = comm.get("session_type", "N/A")
            session_id = comm.get("session_id", "N/A")
            terminate_date = comm.get("terminate_date", "")
            user_login = comm.get("user_login", "N/A")
            local_number = comm.get("local_number", "")
            remote_number = comm.get("remote_number", "")
            start_date = comm.get("start_date", "")
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
            print(f"   📞 Local: {local_number}")
            print(f"   📱 Remote: {remote_number}")
            print(f"   ⏰️ Début: {start_date}")
            print(f"   🕐 Création: {create_date}")
            print()

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Démarrage du monitoring direct CCCP...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Monitoring direct via IndicatorLuT")
    print("Press Ctrl+C pour arrêter\n")

    client = SimpleCallsMonitor("simple_calls_monitor", DEFAULT_IP, DEFAULT_PORT)

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
