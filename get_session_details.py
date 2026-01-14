#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script pour obtenir des détails sur une session spécifique
# Usage: python3 get_session_details.py <session_id>

import sys
from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class SessionDetailsClient(DispatchClient):
    def __init__(self, name, ip, port, login, password, target_session):
        super(SessionDetailsClient, self).__init__(name, ip, port)
        self.login = login
        self.password = password
        self.target_session = target_session

    def on_connection_ok(self, server_version, server_date):
        print("  -> on_connection_ok: version=%s" % server_version)
        self.protocol.sendMessage(message.login, 1, self.login, self.password, 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("  -> on_login_ok: session=%s" % session_id)
        self.configure_views()

    def on_login_failed(self, session_id, reason):
        reason_str = reason
        if isinstance(reason, bytes):
            reason_str = reason.decode("utf-8", errors="replace")
        print("  -> ERROR: login failed - %s" % reason_str)
        self.stop_proxy_info()

    def configure_views(self):
        print("  -> Configuration des vues...")
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()
        print("\nRecherche de la session spécifique...")
        reactor.callLater(3, self.get_session_details)

    def get_session_details(self):
        print("\n" + "=" * 80)
        print("=== DÉTAILS DE LA SESSION %s ===" % self.target_session)
        print("=" * 80)

        # Chercher dans toutes les vues possibles
        self.search_in_communication_sessions()
        self.search_in_outbound_sessions()
        reactor.callLater(2, self.search_extended_info)

    def search_in_communication_sessions(self):
        print("\n--- Recherche dans les sessions de communication ---")
        try:
            view = self.tables[self.communication_session_view_idx][0]
            print(
                "  -> Vue communication_session_view_idx: %d"
                % self.communication_session_view_idx
            )

            # Afficher toutes les sessions disponibles
            all_sessions = list(view.keys())
            print(f"  -> Sessions disponibles ({len(all_sessions)}):")
            for s_id in all_sessions[:10]:  # Limiter à 10 pour la lisibilité
                print(f"     {s_id}")

            # Chercher la session spécifique
            if self.target_session in view:
                data = view.get(self.target_session)
                if data and isinstance(data, list):
                    print(f"\n  ✓ SESSION TROUVÉE dans communication_sessions!")
                    print("  " + "-" * 60)
                    self.display_detailed_session_data(data)
            else:
                print(f"\n  ✗ Session non trouvée dans communication_sessions")

        except Exception as e:
            print(f"  ✗ Erreur: {e}")

    def search_in_outbound_sessions(self):
        print("\n--- Recherche dans les sessions outbound ---")
        try:
            view = self.tables[self.outbound_communication_session_view_idx][0]
            print(
                "  -> Vue outbound_communication_session_view_idx: %d"
                % self.outbound_communication_session_view_idx
            )

            # Afficher quelques sessions outbound
            outbound_sessions = list(view.keys())
            print(f"  -> Sessions outbound disponibles ({len(outbound_sessions)}):")
            for s_id in outbound_sessions[:5]:
                print(f"     {s_id}")

            if self.target_session in view:
                data = view.get(self.target_session)
                if data and isinstance(data, list):
                    print(f"\n  ✓ SESSION TROUVÉE dans outbound_sessions!")
                    print("  " + "-" * 60)
                    self.display_detailed_session_data(data, outbound=True)
            else:
                print(f"\n  ✗ Session non trouvée dans outbound_sessions")

        except Exception as e:
            print(f"  ✗ Erreur: {e}")

    def search_extended_info(self):
        print("\n--- Recherche étendue dans toutes les vues ---")

        # Lister toutes les vues disponibles
        for i, (view, view_type) in enumerate(self.tables):
            try:
                if hasattr(view, "keys"):
                    keys = list(view.keys())
                    if self.target_session in keys:
                        data = view.get(self.target_session)
                        if data and isinstance(data, list):
                            print(
                                f"\n  ✓ SESSION TROUVÉE dans la vue {i} (type: {view_type})!"
                            )
                            print("  " + "-" * 60)
                            self.display_detailed_session_data(data, view_idx=i)
                            break
            except Exception as e:
                continue

        reactor.callLater(2, self.stop_proxy_info)

    def display_detailed_session_data(self, data, outbound=False, view_idx=None):
        print(f"  -> Vue: {view_idx if view_idx is not None else 'N/A'}")
        print(f"  -> Nombre de champs: {len(data)}")

        # Utiliser les champs appropriés selon le type
        if outbound:
            fields = getattr(self, "_outbound_xqueries_list", [])
        elif view_idx == self.communication_session_view_idx:
            fields = getattr(self, "_communication_session_xqueries_list", [])
        else:
            fields = [f"field_{i}" for i in range(len(data))]

        print("\n  DÉTAILS COMPLETS:")
        print("  " + "-" * 60)

        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
            else:
                field_name = f"field_{i}"

            # Nettoyer la valeur pour l'affichage
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except:
                    value = str(value)
            elif value is None:
                value = "NULL"

            # Troncer les longues chaînes
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."

            print("    %-40s: %s" % (field_name, value))

    def on_error(self, failure):
        print("  -> ERROR: %s" % failure)
        self.stop_proxy_info()

    def stop_proxy_info(self):
        print("\n" + "=" * 80)
        print("Recherche terminée.")
        try:
            self.protocol.transport.loseConnection()
        except:
            pass
        reactor.stop()


def get_session_details(target_session):
    ip = "10.199.30.67"
    port = 20101
    login = "supervisor_gtri"
    password = "toto"

    print("Connexion proxy à %s:%s..." % (ip, port))
    print("Login: %s/%s" % (login, password))
    print("Session cible: %s" % target_session)

    client = SessionDetailsClient(
        "session_details", ip, port, login, password, target_session
    )
    client.connect()
    reactor.run()


if __name__ == "__main__":
    target_session = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "session_453@12450.1767694213.Ccxml.vs-pre-prd-cst-fr-307.hostics.fr"
    )
    get_session_details(target_session)
