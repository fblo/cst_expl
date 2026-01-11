#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test pour interroger le CCXML d'un projet CCCP
# Usage: python3 test_ccxml.py <ip> <port> <login> <password> [wait_seconds]

import sys
from twisted.internet import reactor, defer
from cccp.async.ccxml import CcxmlClient
import cccp.protocols.messages.user_control as message_user

class TestCcxmlClient(CcxmlClient):
    def __init__(self, name, ip, port, login, password):
        super(TestCcxmlClient, self).__init__(name, ip, port)
        self.login = login
        self.password = password
        self.session_counter = 1000
        self.event_count = 0

    def on_connection_ok(self, server_version):
        print("  -> on_connection_ok: version=%s" % server_version)
        self.session_counter += 1
        session_id = self.session_counter
        print("  -> Ajout de session %s pour %s" % (session_id, self.login))
        self.add_session(session_id, self.login, self.password, False)

    def get_login_ok(self, session_id, user_id, explorer_id):
        user_id_str = user_id
        if isinstance(user_id, bytes):
            user_id_str = user_id.decode('utf-8', errors='replace')
        print("  -> get_login_ok: session=%s, user_id=%s" % (session_id, user_id_str))
        print("\n" + "="*60)
        print("=== Connexion CCXML réussie =========================")
        print("="*60)
        print("  Session ID: %s" % session_id)
        print("  User ID: %s" % user_id_str)
        self.current_session = session_id
        self.list_info()

    def get_reject(self, session_id, reason):
        print("  -> get_reject: session=%s, reason=%s" % (session_id, reason))
        self.stop()

    def get_server_event(self, session_id, event_name, event_object):
        self.event_count += 1
        event_name_str = event_name
        if isinstance(event_name, bytes):
            event_name_str = event_name.decode('utf-8', errors='replace')
        
        print("\n{:*^60}".format(" ÉVÉNEMENT #%d " % self.event_count))
        print("  Session: %s" % session_id)
        print("  Event: %s" % event_name_str)
        if event_object is not None:
            print("  Object: %s" % event_object)
        print("-" * 60)
        
        # Catégoriser l'événement
        if 'call' in event_name_str.lower() or 'call' in str(event_object).lower():
            print("  📞 [APPEL] Appel téléphonique détecté!")
        elif 'state' in event_name_str.lower():
            print("  📊 [ÉTAT] Changement d'état")
        elif 'supervision' in event_name_str.lower():
            print("  👁️ [SUPERVISION] Événement de supervision")
        elif 'log' in event_name_str.lower():
            print("  📝 [LOG] Message de log")

    def get_logout_ok(self, session_id):
        print("  -> get_logout_ok: session=%s" % session_id)
        self.stop()

    def list_info(self):
        print("\n{:*^60}".format(" INFORMATIONS "))
        print("  En attente d'événements...")
        print("  Appels entrants/sortants, changements d'état, etc.")
        print("  Timeout: %ds (Ctrl+C pour arrêter)" % self.wait_time)
        print("="*60)
        
        reactor.callLater(self.wait_time, self.logout_all)

    def logout_all(self):
        print("\n=== Déconnexion ===")
        for session_id in list(self.connected_sessions.keys()):
            print("  Déconnexion de %s..." % session_id)
            self.logout(session_id)
        reactor.callLater(2, self.stop)

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

def test_ccxml(ip='10.199.30.67', port=20102, login='supervisor_gtri', password='toto', wait=30):
    print("Connexion CCXML à %s:%s..." % (ip, port))
    print("Login: %s/%s" % (login, password))
    print("Attente: %d secondes" % wait)
    
    client = TestCcxmlClient("ccxml_test", ip, port, login, password)
    client.wait_time = wait
    client.connect()
    reactor.run()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20102
    login = sys.argv[3] if len(sys.argv) > 3 else "supervisor_gtri"
    password = sys.argv[4] if len(sys.argv) > 4 else "toto"
    wait = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    
    test_ccxml(ip, port, login, password, wait)
