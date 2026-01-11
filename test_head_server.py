#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test pour interroger un serveur vocal CCCP
# Usage: python3 test_head_server.py <ip> <port> <path>

import sys
from twisted.internet import reactor, defer
from cccp.async.head import HeadClient

class TestHeadClient(HeadClient):
    def __init__(self, name, ip, port=20000):
        super(TestHeadClient, self).__init__(name, ip, port)
        self.results = []

    def on_connection_ok(self, server_version, server_date):
        print("  -> on_connection_ok: version=%s" % server_version)
        super(TestHeadClient, self).on_connection_ok(server_version, server_date)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("  -> on_login_ok: session=%s" % session_id)
        super(TestHeadClient, self).on_login_ok(session_id, user_id, explorer_id)

    def on_use_default_namespaces_index_ok(self):
        print("  -> on_use_default_namespaces_index_ok")
        super(TestHeadClient, self).on_use_default_namespaces_index_ok()

    def connect_done(self, success):
        print("  -> connect_done: %s" % success)
        if success:
            path = sys.argv[3] if len(sys.argv) > 3 else ""
            if path:
                self.list_children(path)
            else:
                print("Usage: python3 test_head_server.py <ip> <port> <path>")
                self.stop()

    def list_children(self, path):
        print("\nListe des children de '%s'..." % path)
        d = self.get_children(path)
        d.addCallback(self.on_children_received)
        d.addErrback(self.on_error)

    def on_children_received(self, nodes):
        print("  -> on_children_received")
        print("  Nombre de nodes: %d" % len(nodes))
        for node in nodes:
            # Afficher les attributs disponibles
            attrs = dir(node)
            print("    - %s (id=%s)" % (node.name, node.id))
            print("      Attributs: %s" % [a for a in attrs if not a.startswith('_')])
        self.stop()

    def on_error(self, failure):
        print("  -> ERROR: %s" % failure)
        self.stop()

    def stop(self):
        print("\nDéconnexion...")
        try:
            self.protocol.transport.loseConnection()
        except:
            pass
        reactor.stop()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.25"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    
    print("Connexion à %s:%s..." % (ip, port))
    client = TestHeadClient("test", ip, port)
    client.connect()
    reactor.run()
