#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class CallTester(DispatchClient):
    def __init__(self, name, ip, port):
        super(CallTester, self).__init__(name, ip, port)

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur CCCP {self.ip}:{self.port}")
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

        # Tester plusieurs filtres pour voir s'il y a des communications
        self.test_communications()

    def test_communications(self):
        print("\n" + "=" * 60)
        print("📞 TEST DES COMMUNICATIONS AVEC DIFFÉRENTS FILTRES")
        print("=" * 60)

        # Filtre 1: Toutes les sessions avec terminate_date non vide
        self.test_filter(
            "test_terminated", ".[terminate_date ne '']", "Sessions terminées"
        )

        # Filtre 2: Toutes les sessions type 1 (inbound)
        self.test_filter(
            "test_type1", ".[session_type eq '1']", "Sessions type 1 (inbound)"
        )

        # Filtre 3: Toutes les sessions sans filtrer
        self.test_filter("test_all", "", "Toutes les sessions")

        # Filtre 4: Sessions de superviseurs
        self.test_filter(
            "test_supervisors",
            ".[sessions/last/session/profile_name contains 'Superviseur']",
            "Sessions superviseurs",
        )

        print("\n" + "=" * 60)
        print("🔚 TEST TERMINÉ - ARRÊT")
        print("=" * 60)
        self.stop()

    def test_filter(self, view_name, filter_str, description):
        print(f"\n📋 {description}:")
        print(f"🔍 Filtre: {filter_str}")

        try:
            view_idx = self.start_view(
                view_name,
                "sessions",
                [
                    "create_date",
                    "session_type",
                    "session_id",
                    "terminate_date",
                    "user.login",
                    "manager_session.user.login",
                    "sessions.last.session.profile_name",
                    "sessions.last.session.logged",
                    "sessions.last.session.current_mode",
                    "attributes.local_number.value",
                    "attributes.remote_number.value",
                    "start_date",
                    "management_effective_date",
                    "last_state_name",
                    "last_state_display_name",
                    "last_task_display_name",
                    "last_task_name",
                ],
                filter_str,
            )

            print(f"✅ Vue créée (ID: {view_idx})")

            # Attendre un peu pour que les données arrivent
            reactor.callLater(3, self.display_view_data, view_idx, view_name)

        except Exception as e:
            print(f"❌ Erreur création vue: {e}")

    def display_view_data(self, view_idx, view_name):
        try:
            view = self.tables.get(view_idx)
            if view and view[0]:
                table_data = view[0]
                print(f"📊 {len(table_data)} entrées trouvées:")

                if len(table_data) > 0:
                    # Afficher les 5 premières
                    for i, (session_id, data) in enumerate(table_data.items()):
                        if i < 5:  # Limiter à 5 pour la lisibilité
                            print(f"\n📞 Entrée {i + 1}: {session_id}")
                            for j, value in enumerate(data):
                                field_name = f"Champ_{j}"
                                print(f"   {field_name}: {value}")
                        elif i == 5:
                            print(f"\n... et encore {len(table_data) - 5} entrées")
                            break
                else:
                    print("   📭 Aucune entrée")
            else:
                print("❌ Pas de données dans la vue")

        except Exception as e:
            print(f"❌ Erreur lecture données: {e}")


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Testeur de communications CCCP")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("Test de différents filtres pour trouver les appels")
    print("Press Ctrl+C pour arrêter\n")

    client = CallTester("call_tester", DEFAULT_IP, DEFAULT_PORT)

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
