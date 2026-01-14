#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class SimpleConnectionTest(DispatchClient):
    def __init__(self, name, ip, port):
        super(SimpleConnectionTest, self).__init__(name, ip, port)

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur {self.ip}:{self.port}")
        print(f"Version serveur: {server_version}")
        print(f"Date serveur: {server_date}")

        # Essayer de se login
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print(f"✅ Login OK - Session ID: {session_id}")
        print(f"User ID: {user_id}")
        print(f"Explorer ID: {explorer_id}")

        # Essayer d'utiliser les namespaces par défaut
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("✅ Index par défaut initialisé")
        print("🎉 Connexion complète réussie!")
        self.stop()

    def on_use_default_namespaces_index_failed(self, error_id, error_message):
        print(f"❌ Erreur index: {error_message}")
        self.stop()

    def on_connection_failed(self, reason):
        print(f"❌ Connexion failed: {reason}")
        self.stop()

    def stop(self):
        print("\n👋 Fin du test")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Test de connexion simple...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print()

    client = SimpleConnectionTest("test_client", DEFAULT_IP, DEFAULT_PORT)

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
