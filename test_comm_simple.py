#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class SimpleIndicatorChecker(DispatchClient):
    def __init__(self, name, ip, port):
        super(SimpleIndicatorChecker, self).__init__(name, ip, port)

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur CCCP {self.ip}:{self.port}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print(f"✅ Login OK")
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("📞 Test de récupération des communications...")

        # Créer une vue simple pour voir ce qu'on a
        try:
            self.communication_view_idx = self.start_view(
                "test_comms",
                "sessions",
                [
                    "create_date",
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
                    "last_state_name",
                    "last_state_display_name",
                ],
                ".[session_type ne 3 and terminate_date eq '']",
            )
        except Exception as e:
            print(f"❌ Erreur création vue: {e}")
            self.stop()

        # Lancer la récupération
        reactor.callLater(2, self.check_communications)

    def check_communications(self):
        try:
            view = self.tables.get(self.communication_view_idx)
            if view and view[0]:
                table_data = view[0]
                print(f"\n{'=' * 60}")
                print(f"📞 COMMUNICATIONS TROUVÉES: {len(table_data)}")
                print("=" * 60)

                if len(table_data) > 0:
                    print("\n📊 DÉTAIL DES COMMUNICATIONS:")
                    for i, (session_id, data) in enumerate(table_data.items(), 1):
                        print(f"\n📞 Communication {i}:")
                        print(f"   🆔 Session ID: {session_id}")
                        print(f"   📋 Type: {data[1] if len(data) > 1 else 'N/A'}")
                        print(f"   🔚 Terminé: {data[3] if len(data) > 3 else 'N/A'}")
                        print(
                            f"   👤 User: {data[4] if len(data) > 4 else data[5] if len(data) > 5 else 'N/A'}"
                        )
                        print(f"   📱 Local: {data[7] if len(data) > 7 else 'N/A'}")
                        print(f"   📞 Remote: {data[8] if len(data) > 8 else 'N/A'}")
                        print(f"   🏷️ Queue: {data[9] if len(data) > 9 else 'N/A'}")
                        print(
                            f"   ⏰️ Start: {data[10] if len(data) > 10 else data[11] if len(data) > 11 else 'N/A'}"
                        )
                        print(f"   🕐 Create: {data[12] if len(data) > 12 else 'N/A'}")
                        print(
                            f"   🎙️ Enregistrement: {data[13] if len(data) > 13 else 'N/A'}"
                        )
                        print(
                            f"   📞 State: {data[14] if len(data) > 14 else data[15] if len(data) > 15 else 'N/A'}"
                        )

                        # Afficher tous les champs disponibles
                        print(f"   📋 Tous les champs ({len(data)}):")
                        for j, value in enumerate(data):
                            print(f"      [{j}]: {value}")
                else:
                    print("   📭 Aucune communication trouvée")

            else:
                print("   ❌ Pas de données dans la vue")

        except Exception as e:
            print(f"❌ Erreur lecture données: {e}")
            import traceback

            traceback.print_exc()

        print(f"\n{'=' * 60}")
        print("👋 Test terminé")
        self.stop()

    def stop(self):
        if reactor.running:
            reactor.stop()


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🔍 Test simple des communications CCCP...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")

    client = SimpleIndicatorChecker("comm_checker", DEFAULT_IP, DEFAULT_PORT)

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
