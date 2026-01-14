#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script simplifié pour obtenir des détails sur une session spécifique
import sys
from twisted.internet import reactor
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class SimpleSessionClient(DispatchClient):
    def __init__(self, name, ip, port, login, password, target_session):
        super(SimpleSessionClient, self).__init__(name, ip, port)
        self.login = login
        self.password = password
        self.target_session = target_session

    def on_connection_ok(self, server_version, server_date):
        print("Connexion établie - version: %s" % server_version)
        self.protocol.sendMessage(message.login, 1, self.login, self.password, 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("Login réussi - session: %s" % session_id)
        self.connect_done(True)
        self.connection_finished()
        reactor.callLater(3, self.search_session)

    def on_login_failed(self, session_id, reason):
        reason_str = reason
        if isinstance(reason, bytes):
            reason_str = reason.decode("utf-8", errors="replace")
        print("ERREUR: login failed - %s" % reason_str)
        reactor.stop()

    def search_session(self):
        print("\nRecherche de la session: %s" % self.target_session)
        print("=" * 70)

        try:
            # Chercher dans les sessions de communication
            view = self.tables[self.communication_session_view_idx][0]
            all_sessions = list(view.keys())
            print("Sessions communication disponibles (%d):" % len(all_sessions))
            for s_id in all_sessions:
                print("  %s" % s_id)

            if self.target_session in view:
                data = view.get(self.target_session)
                if data and isinstance(data, list):
                    print("\n✓ SESSION TROUVÉE!")
                    print("-" * 70)
                    self.display_session_data(data)
                else:
                    print("\nSession trouvée mais sans données")
            else:
                print("\n✗ Session non trouvée")

        except Exception as e:
            print("ERREUR: %s" % e)

        reactor.stop()

    def display_session_data(self, data):
        fields = getattr(self, "_communication_session_xqueries_list", [])
        print("Nombre de champs: %d" % len(data))
        print("\nDétails:")

        for i, value in enumerate(data):
            field_name = fields[i] if i < len(fields) else "field_%d" % i

            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except:
                    value = str(value)
            elif value is None:
                value = "NULL"
            elif isinstance(value, str) and len(value) > 150:
                value = value[:150] + "..."

            print("  %-35s: %s" % (field_name, value))


def main():
    target_session_arg = sys.argv[1] if len(sys.argv) > 1 else "453"

    # Convertir en entier si possible
    try:
        target_session = int(target_session_arg)
        print("Recherche détaillée de session (ID numérique)")
    except ValueError:
        target_session = target_session_arg
        print("Recherche détaillée de session (chaîne)")

    print("Session cible: %s (%s)" % (target_session, type(target_session).__name__))

    client = SimpleSessionClient(
        "search", "10.199.30.67", 20101, "supervisor_gtri", "toto", target_session
    )
    client.connect()
    reactor.run()


if __name__ == "__main__":
    main()
