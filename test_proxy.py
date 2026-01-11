#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test pour interroger le proxy d'un projet CCCP
# Usage: python3 test_proxy.py <ip> <port> <login> <password> [wait_seconds]

import sys
from twisted.internet import reactor, defer
from cccp.async.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message

class TestProxyClient(DispatchClient):
    def __init__(self, name, ip, port, login, password):
        super(TestProxyClient, self).__init__(name, ip, port)
        self.login = login
        self.password = password

    def on_connection_ok(self, server_version, server_date):
        print("  -> on_connection_ok: version=%s" % server_version)
        self.protocol.sendMessage(message.login, 1, self.login, self.password, 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("  -> on_login_ok: session=%s" % session_id)
        # Le proxy peut ne pas supporter use_default_namespaces_index
        # On configure directement les vues
        self.configure_views()

    def on_login_failed(self, session_id, reason):
        reason_str = reason
        if isinstance(reason, bytes):
            reason_str = reason.decode('utf-8', errors='replace')
        print("  -> ERROR: login failed - %s" % reason_str)
        self.stop_proxy_info()

    def configure_views(self):
        print("  -> Configuration des vues...")
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()
        print("\nAttente de 5 secondes pour mise à jour des vues...")
        reactor.callLater(5, self.list_proxy_info)

    def list_proxy_info(self):
        print("\n" + "="*60)
        print("=== Proxy MPU_PREPROD - Tableau de bord =============")
        print("="*60)
        
        # Details des queues
        print("\n{:*^60}".format(" QUEUES (%d) " % len(self.get_queues())))
        for q_id in self.get_queues()[:20]:
            view = self.tables[self.queue_view_idx][0]
            data = view.get(q_id)
            if data and isinstance(data, list):
                info = self._format_queue_data(data)
                if info:
                    print("\n  [Queue %s] %s" % (q_id, info.get('display_name', 'N/A')))
                    print("  " + "-" * 50)
                    for key, value in info.items():
                        if key != 'display_name' and value is not None:
                            print("    %-30s: %s" % (key, value))
        
        # Details des utilisateurs
        print("\n{:*^60}".format(" UTILISATEURS (%d) " % len(self.get_users())))
        for u_id in self.get_users()[:20]:
            view = self.tables[self.user_view_idx][0]
            data = view.get(u_id)
            if data and isinstance(data, list):
                info = self._format_user_data(data)
                if info:
                    print("\n  [Utilisateur %s] %s (%s)" % (u_id, info.get('login', 'N/A'), info.get('name', 'N/A')))
                    print("  " + "-" * 50)
                    for key, value in info.items():
                        if key not in ['login', 'name'] and value is not None:
                            print("    %-30s: %s" % (key, value))
        
        # Details des sessions de communication
        print("\n{:*^60}".format(" SESSIONS (%d) " % len(self.get_communication_sessions())))
        sessions = self.get_communication_sessions()
        if sessions:
            for s_id in sessions[:20]:
                view = self.tables[self.communication_session_view_idx][0]
                data = view.get(s_id)
                if data and isinstance(data, list):
                    info = self._format_session_data(data)
                    if info:
                        print("\n  [Session %s]" % s_id)
                        print("  " + "-" * 50)
                        for key, value in info.items():
                            if value is not None:
                                print("    %-30s: %s" % (key, value))
        else:
            print("  Aucune session active")

        # Details des outbound sessions
        print("\n{:*^60}".format(" SESSIONS OUTBOUND (%d) " % len(self.get_outbound_sessions())))
        outbound = self.get_outbound_sessions()
        if outbound:
            for s_id in outbound[:20]:
                view = self.tables[self.outbound_communication_session_view_idx][0]
                data = view.get(s_id)
                if data and isinstance(data, list):
                    print("\n  [Outbound %s]" % s_id)
                    print("    Données: %s" % str(data)[:200])
        else:
            print("  Aucune session outbound active")

        print("\n" + "="*60)
        self.stop_proxy_info()

    def _format_queue_data(self, data):
        if not data or len(data) < 2:
            return None
        result = {}
        fields = self._service_xqueries_list
        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        pass
                result[field_name] = value
        return result

    def _format_user_data(self, data):
        if not data or len(data) < 2:
            return None
        result = {}
        fields = self._user_xqueries_list
        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        pass
                result[field_name] = value
        return result
    
    def _format_session_data(self, data):
        if not data or len(data) < 2:
            return None
        result = {}
        fields = self._communication_session_xqueries_list
        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        pass
                result[field_name] = value
        return result

    def get_queues(self):
        try:
            view = self.tables[self.queue_view_idx][0]
            return list(view.keys())
        except:
            return []

    def get_users(self):
        try:
            view = self.tables[self.user_view_idx][0]
            return list(view.keys())
        except:
            return []

    def get_communication_sessions(self):
        try:
            view = self.tables[self.communication_session_view_idx][0]
            return list(view.keys())
        except:
            return []
    
    def get_outbound_sessions(self):
        try:
            view = self.tables[self.outbound_communication_session_view_idx][0]
            return list(view.keys())
        except:
            return []

    def on_error(self, failure):
        print("  -> ERROR: %s" % failure)
        self.stop_proxy_info()

    def stop_proxy_info(self):
        print("\nDéconnexion...")
        try:
            self.protocol.transport.loseConnection()
        except:
            pass
        reactor.stop()

def test_proxy(ip='10.199.30.67', port=20101, login='supervisor_gtri', password='toto', wait=3):
    print("Connexion proxy à %s:%s..." % (ip, port))
    print("Login: %s/%s" % (login, password))
    
    client = TestProxyClient("proxy_test", ip, port, login, password)
    client.connect()
    reactor.run()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20101
    login = sys.argv[3] if len(sys.argv) > 3 else "supervisor_gtri"
    password = sys.argv[4] if len(sys.argv) > 4 else "toto"
    wait = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    
    test_proxy(ip, port, login, password, wait)
