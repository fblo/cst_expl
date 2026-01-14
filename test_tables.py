#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class TableExplorer(DispatchClient):
    def __init__(self, name, ip, port):
        super(TableExplorer, self).__init__(name, ip, port)

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
        # Essayer de lister toutes les tables
        reactor.callLater(1, self.list_tables)

    def list_tables(self):
        print("\n" + "=" * 60)
        print("📋 LISTE DES TABLES DISPONIBLES")
        print("=" * 60)

        try:
            # Essayer quelques noms de tables probables
            tables_to_test = [
                "communications_sessions",
                "sessions",
                "communications_tasks",
                "communications_queues",
                "tasks",
                "users_sessions",
                "outbound_communications_sessions",
                "outbound_daily_communications_sessions",
            ]

            for table_name in tables_to_test:
                try:
                    # Créer une vue simple pour tester
                    view_idx = self.start_view(
                        f"test_{table_name}",
                        table_name,
                        ["create_date"],  # Champ simple
                        "",  # Pas de filtre
                    )
                    print(f"✅ Table '{table_name}' - Vue ID: {view_idx}")
                except Exception as e:
                    print(f"❌ Table '{table_name}' - Erreur: {e}")

        except Exception as e:
            print(f"❌ Erreur générale: {e}")

        print("\n" + "=" * 60)
        print("🔚 TEST D'UNE VUE AVEC PLUS DE CHAMPS")
        print("=" * 60)

        try:
            # Tester une vue avec plus de champs sur sessions
            self.session_view_idx = self.start_view(
                "test_sessions_detailed",
                "sessions",
                [
                    "session_id",
                    "create_date",
                    "terminate_date",
                    "session_type",
                    "user.login",
                    "manager_session.user.login",
                    "sessions.last.session.current_mode",
                    "sessions.last.session.logged",
                    "attributes.local_number.value",
                    "attributes.remote_number.value",
                ],
                "",  # Pas de filtre pour voir tout
            )

            print(f"✅ Vue sessions détaillée - Vue ID: {self.session_view_idx}")
            print("⏳ Attente 3 secondes pour récupérer les données...")
            reactor.callLater(3, self.display_session_data)

        except Exception as e:
            print(f"❌ Erreur création vue détaillée: {e}")
            self.stop()

    def display_session_data(self):
        try:
            view = self.tables.get(self.session_view_idx)
            if view and view[0]:
                table_data = view[0]
                print(f"\n📊 {len(table_data)} entrées dans la table sessions:")
                print("=" * 50)

                if len(table_data) == 0:
                    print("   📭 Aucune entrée trouvée")
                    print("\n⚠️ Résumé:")
                    print("   - La table 'sessions' existe mais est vide")
                    print("   - Soit il n'y a pas de communications en cours")
                    print("   - Soit les communications sont dans une autre table")
                else:
                    print("   📝 Détails des 3 premières entrées:")

                    for i, (session_id, data) in enumerate(table_data.items()):
                        if i < 3:
                            print(f"\n📞 Session {i + 1}: {session_id}")
                            for j, value in enumerate(data):
                                if j < len(
                                    [
                                        "session_id",
                                        "create_date",
                                        "terminate_date",
                                        "session_type",
                                        "user.login",
                                        "manager_session.user.login",
                                        "sessions.last.session.current_mode",
                                        "sessions.last.session.logged",
                                        "attributes.local_number.value",
                                        "attributes.remote_number.value",
                                    ]
                                ):
                                    field_names = [
                                        "session_id",
                                        "create_date",
                                        "terminate_date",
                                        "session_type",
                                        "user.login",
                                        "manager_session.user.login",
                                        "sessions.last.session.current_mode",
                                        "sessions.last.session.logged",
                                        "attributes.local_number.value",
                                        "attributes.remote_number.value",
                                    ]
                                    field_name = (
                                        field_names[j]
                                        if j < len(field_names)
                                        else f"field_{j}"
                                    )
                                    print(f"      {field_name}: {value}")
                    else:
                        print(f"\n... et encore {len(table_data) - 3} entrées")

                print("\n" + "=" * 60)
                print("🔍 RECHERCHE D'APPELS POSSIBLES")
                print("=" * 60)

                call_related_sessions = []
                for session_id, data in table_data.items():
                    if data and len(data) > 10:  # Si assez de champs
                        # Rechercher des champs liés aux appels
                        mode = (
                            data[6] if len(data) > 6 else ""
                        )  # sessions.last.session.current_mode
                        logged = (
                            data[7] if len(data) > 7 else ""
                        )  # sessions.last.session.logged
                        local_num = (
                            data[8] if len(data) > 8 else ""
                        )  # attributes.local_number.value
                        remote_num = (
                            data[9] if len(data) > 9 else ""
                        )  # attributes.remote_number.value

                        if any([local_num, remote_num]) or any(
                            word in mode.lower()
                            for word in ["call", "appel", "communication"]
                        ):
                            call_related_sessions.append((session_id, data))

                print(
                    f"📞 Sessions potentiellement liées à des appels: {len(call_related_sessions)}"
                )

                for session_id, data in call_related_sessions[:5]:
                    mode = data[6] if len(data) > 6 else ""
                    logged = data[7] if len(data) > 7 else "False"
                    local_num = data[8] if len(data) > 8 else ""
                    remote_num = data[9] if len(data) > 9 else ""

                    print(f"\n📞 Session: {session_id}")
                    print(f"   📞 Mode: {mode}")
                    print(f"   ✅ Connecté: {logged}")
                    print(f"   📞 Local: {local_num}")
                    print(f"   📝 Remote: {remote_num}")

            else:
                print("❌ Pas de données dans la vue")

        except Exception as e:
            print(f"❌ Erreur lecture données: {e}")
            import traceback

            traceback.print_exc()

        print("\n" + "=" * 60)
        print("👋 FIN D'EXPLORATION")
        print("=" * 60)
        self.stop()

    def stop(self):
        print("\n👋 Arrêt de l'explorateur")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🔍 Explorateur de tables CCCP...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("Test de la disponibilité des tables de communications")
    print("Press Ctrl+C pour arrêter\n")

    client = TableExplorer("table_explorer", DEFAULT_IP, DEFAULT_PORT)

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
