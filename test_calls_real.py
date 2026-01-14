#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class CallMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(CallMonitor, self).__init__(name, ip, port)
        self.cycle_count = 0

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur {self.ip}:{self.port}")
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
        reactor.callLater(1, self.start_monitoring)

    def start_monitoring(self):
        print("📞 Démarrage monitoring des appels...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 60}")
        print(f"📞 CYCLE {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        try:
            # Utiliser le message de communication pour obtenir les appels
            self.protocol.sendMessage(
                message.get_communications,
                1,  # message_id
                [],  # profiles_list (vide = tous)
                [],  # queues_list (vide = toutes)
                [],  # users_list (vide = tous)
                [],  # states_list (vide = tous)
                None,  # start_time
                None,  # stop_time
                [],  # communication_ids_list
                [],  # session_ids_list
                False,  # include_records
                1000,  # limit
                0,  # offset
            )

        except Exception as e:
            print(f"❌ Erreur monitoring: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring
        reactor.callLater(10, self.monitor_loop)

    def on_get_communications_ok(self, communications):
        """Affiche les communications reçues"""
        if not communications or len(communications) == 0:
            print("   📭 Aucune communication trouvée")
            return

        print(f"📊 {len(communications)} communication(s) trouvée(s):")
        print()

        for i, comm in enumerate(
            communications[:10], 1
        ):  # Limiter à 10 pour l'affichage
            self.display_single_communication(i, comm)

        if len(communications) > 10:
            print(f"... et {len(communications) - 10} autres communications")

    def on_get_communications_failed(self, error_id, error_message):
        print(f"❌ Erreur get_communications: {error_message}")

    def display_single_communication(self, index, comm):
        """Affiche une communication individuelle"""
        try:
            comm_id = comm.get("id", "N/A")
            channel = comm.get("channel", "N/A")
            comm_type = comm.get("type", "N/A")

            # Dates
            start_date = comm.get("start_date", "")
            stop_date = comm.get("stop_date", "")
            create_date = comm.get("create_date", "")

            # Numéros
            from_field = comm.get("from", "")
            to_field = comm.get("to", "")

            # Nettoyer les numéros
            if from_field and from_field.startswith("tel:"):
                from_field = from_field[4:]
            if to_field and to_field.startswith("tel:"):
                to_field = to_field[4:]

            # Statut
            status = "🟢 ACTIF" if not stop_date else "🔴 TERMINÉ"

            # Info utilisateur/session
            session = comm.get("session", {})
            if session:
                user = session.get("user", {})
                user_login = user.get("login", "N/A") if user else "N/A"
                profile_name = session.get("profile_name", "N/A")
            else:
                user_login = "N/A"
                profile_name = "N/A"

            print(f"📞 {index}. {status}")
            print(f"   📋 ID: {comm_id}")
            print(f"   📊 Canal: {channel} - Type: {comm_type}")
            print(f"   👤 Utilisateur: {user_login} (Profile: {profile_name})")
            print(f"   📱 De: {from_field or 'N/A'}")
            print(f"   📝 À: {to_field or 'N/A'}")
            print(f"   ⏰️ Début: {start_date or create_date}")
            if stop_date:
                print(f"   🕐 Fin: {stop_date}")
            print()

        except Exception as e:
            print(f"   ❌ Erreur affichage comm: {e}")
            print(f"   📄 Debug: {str(comm)[:200]}")
            print()

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Démarrage du monitoring des appels...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Utilisation de get_communications pour récupérer les appels")
    print("Press Ctrl+C pour arrêter\n")

    client = CallMonitor("call_monitor", DEFAULT_IP, DEFAULT_PORT)

    try:
        client.connect()
        reactor.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé")
        client.stop()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
