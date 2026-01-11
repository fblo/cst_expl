#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test pour interroger le dispatch d'un projet CCCP
# Usage: python3 test_dispatch_project.py <ip> <port> [wait_seconds]

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class TestDispatchClient(DispatchClient):
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
        print("\nAttente de 3 secondes pour mise à jour des vues...")
        reactor.callLater(3, self.list_project_info)

    def list_project_info(self):
        print("\n" + "=" * 60)
        print("=== Projet MPU_PREPROD - Tableau de bord ==========")
        print("=" * 60)

        # Details des queues
        print("\n{:*^60}".format(" QUEUES (%d) " % len(self.get_queues())))
        for q_id in self.get_queues()[:20]:
            view = self.tables[self.queue_view_idx][0]
            data = view.get(q_id)
            if data and isinstance(data, list):
                info = self._format_queue_data(data)
                if info:
                    print("\n  [Queue %s] %s" % (q_id, info.get("display_name", "N/A")))
                    print("  " + "-" * 50)
                    for key, value in info.items():
                        if key != "display_name" and value is not None:
                            print("    %-30s: %s" % (key, value))

        # Details des utilisateurs
        print("\n{:*^60}".format(" UTILISATEURS (%d) " % len(self.get_users())))
        for u_id in self.get_users()[:20]:
            view = self.tables[self.user_view_idx][0]
            data = view.get(u_id)
            if data and isinstance(data, list):
                info = self._format_user_data(data)
                if info:
                    print(
                        "\n  [Utilisateur %s] %s (%s)"
                        % (u_id, info.get("login", "N/A"), info.get("name", "N/A"))
                    )
                    print("  " + "-" * 50)
                    for key, value in info.items():
                        if key not in ["login", "name"] and value is not None:
                            print("    %-30s: %s" % (key, value))

        # Details des tasks
        print("\n{:*^60}".format(" TASKS (%d) " % len(self.get_tasks())))
        tasks = self.get_tasks()
        if tasks:
            for t_id in tasks[:20]:
                view = self.tables[self.communication_task_view_idx][0]
                data = view.get(t_id)
                if data:
                    print("\n  [Task %s]" % t_id)
                    print("    Données: %s" % str(data)[:200])
        else:
            print("  Aucune task active")

        print("\n" + "=" * 60)
        self.stop()

    def _format_queue_data(self, data):
        """Formate les données d'une queue avec les noms de champs."""
        if not data or len(data) < 2:
            return None

        result = {}
        fields = self._service_xqueries_list

        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
                # Convertir bytes en str pour l'affichage
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8")
                    except:
                        pass
                result[field_name] = value

        return result

    def _format_user_data(self, data):
        """Formate les données d'un utilisateur avec les noms de champs."""
        if not data or len(data) < 2:
            return None

        result = {}
        fields = self._user_xqueries_list

        for i, value in enumerate(data):
            if i < len(fields):
                field_name = fields[i]
                # Convertir bytes en str pour l'affichage
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8")
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


def test_dispatch_project(ip="10.199.30.67", port=20103, wait=3):
    print("Connexion dispatch à %s:%s..." % (ip, port))
    print("Projet: MPU_PREPROD")
    print("Login: admin/admin")

    client = TestDispatchClient("dispatch_test", ip, port)
    client.connect()
    reactor.run()


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.199.30.67"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20103
    wait = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    test_dispatch_project(ip, port, wait)
