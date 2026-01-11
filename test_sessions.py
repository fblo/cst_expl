#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test pour voir les sessions actives sur le dispatch
# Usage: python3 test_sessions.py <ip> <port> [wait_seconds]

import sys
from twisted.internet import reactor, defer
from cccp.async.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message

class TestSessionsClient(DispatchClient):
    def on_connection_ok(self, server_version, server_date):
        print("  -> on_connection_ok: version=%s" % server_version)
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print("  -> on_login_ok: session=%s" % session_id)
        self.protocol.sendMessage(message.use_default_namespaces_index)

    def on_login_failed(self, session_id, reason):
        print("  -> ERROR: login failed - %s" % reason)
        self.stop()

    def on_use_default_namespaces_index_ok(self):
        print("  -> on_use_default_namespaces_index_ok")
        if self.d_connect:
            self.d_connect.callback(True)
        else:
            self.connect_done(True)
        self.connection_finished()
        print("\nAttente de 5 secondes pour mise à jour des vues...")
        reactor.callLater(5, self.list_sessions)

    def list_sessions(self):
        print("\n" + "="*70)
        print("=== Sessions actives - Projet MPU_PREPROD ===================")
        print("="*70)
        
        # Sessions de communication
        print("\n{:*^70}".format(" SESSIONS DE COMMUNICATION (%d) " % len(self.get_communication_sessions())))
        sessions = self.get_communication_sessions()
        if sessions:
            for s_id in sessions:
                view = self.tables[self.communication_session_view_idx][0]
                data = view.get(s_id)
                if data and isinstance(data, list):
                    info = self._format_session_data(data)
                    if info:
                        print("\n  [Session %s]" % s_id)
                        print("  " + "-" * 60)
                        for key, value in info.items():
                            if value is not None and value != '':
                                # Tronquer les valeurs trop longues
                                value_str = str(value)
                                if len(value_str) > 50:
                                    value_str = value_str[:50] + "..."
                                print("    %-35s: %s" % (key, value_str))
        else:
            print("  Aucune session active")

        # Sessions outbound
        print("\n{:*^70}".format(" SESSIONS OUTBOUND (%d) " % len(self.get_outbound_sessions())))
        outbound = self.get_outbound_sessions()
        if outbound:
            for s_id in outbound:
                view = self.tables[self.outbound_communication_session_view_idx][0]
                data = view.get(s_id)
                if data and isinstance(data, list):
                    info = self._format_outbound_data(data)
                    if info:
                        print("\n  [Outbound %s]" % s_id)
                        print("  " + "-" * 60)
                        for key, value in info.items():
                            if value is not None and value != '':
                                value_str = str(value)
                                if len(value_str) > 50:
                                    value_str = value_str[:50] + "..."
                                print("    %-35s: %s" % (key, value_str))
        else:
            print("  Aucune session outbound")

        # Tasks en cours
        print("\n{:*^70}".format(" TASKS EN COURS (%d) " % len(self.get_tasks())))
        tasks = self.get_tasks()
        if tasks:
            for t_id in tasks:
                view = self.tables[self.communication_task_view_idx][0]
                data = view.get(t_id)
                if data and isinstance(data, list):
                    info = self._format_task_data(data)
                    if info:
                        print("\n  [Task %s]" % t_id)
                        print("  " + "-" * 60)
                        for key, value in info.items():
                            if value is not None and value != '':
                                value_str = str(value)
                                if len(value_str) > 50:
                                    value_str = value_str[:50] + "..."
                                print("    %-35s: %s" % (key, value_str))
        else:
            print("  Aucune task en cours")

        # Résumé
        print("\n" + "="*70)
        print("RÉSUMÉ:")
        print("  - Sessions de communication: %d" % len(sessions))
        print("  - Sessions outbound: %d" % len(outbound))
        print("  - Tasks en cours: %d" % len(tasks))
        print("="*70)
        
        self.stop()

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

    def _format_outbound_data(self, data):
        if not data or len(data) < 2:
            return None
        result = {}
        fields = self._outbound_communication_session_xqueries_list
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
    
    def _format_task_data(self, data):
        if not data or len(data) < 2:
            return None
        result = {}
        fields = self._communication_task_xqueries_list
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
    
    def get_tasks(self):
        try:
            view = self.tables[self.communication_task_view_idx][0]
            return list(view.keys())
        except:
            return []

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

def test_sessions(ip='10.199.30.67', port=20103, wait=5):
    print("Connexion dispatch à %s:%s..." % (ip, port))
    print("Recherche des sessions actives...")
    
    client = TestSessionsClient("sessions_test", ip, port)
    client.connect()
    reactor.run()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20103
    wait = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    test_sessions(ip, port, wait)
