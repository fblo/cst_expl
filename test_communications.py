#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class CommunicationMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(CommunicationMonitor, self).__init__(name, ip, port)
        self.cycle_count = 0
        self.communication_view_idx = None
        self.queue_view_idx = None
        self.task_view_idx = None

    def connect_done(self, result_value):
        """Override to set up communication views"""
        print("🔧 Configuration des vues de communication...")

        # Créer les vues comme dans DispatchClient
        self.communication_session_view_idx = self.start_view(
            "sessions",
            "communications_sessions",
            self._communication_session_xqueries_list,
            ".[connections/last/call_id ne '' and session_type ne 3]",
        )

        self.communication_queue_view_idx = self.start_view(
            "file_tasks",
            "communications_queues",
            self._communication_queue_xqueries_list,
            ".[terminate_date eq '']",
        )

        self.communication_task_view_idx = self.start_view(
            "tasks",
            "communications_tasks",
            self._communication_task_xqueries_list,
            "",
        )

        print(
            f"✅ Vues créées: sessions={self.communication_session_view_idx}, queues={self.communication_queue_view_idx}, tasks={self.communication_task_view_idx}"
        )

        # Démarrer le monitoring après 2 secondes
        reactor.callLater(2, self.start_monitoring)

    def start_monitoring(self):
        print("📞 Démarrage monitoring des communications...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 60}")
        print(f"📞 CYCLE {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        try:
            # Lancer les requêtes sur les différentes vues
            if self.communication_session_view_idx:
                print("🔍 Recherche des sessions de communication...")
                self.query_list(
                    self.communication_session_view_idx,
                    "sessions",
                    ".[connections/last/call_id ne '' and session_type ne 3]",
                )

            if self.communication_queue_view_idx:
                print("🔍 Recherche des files de communication...")
                self.query_list(
                    self.communication_queue_view_idx,
                    "file_tasks",
                    ".[terminate_date eq '']",
                )

        except Exception as e:
            print(f"❌ Erreur monitoring: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring
        reactor.callLater(10, self.monitor_loop)

    def _communication_session_xqueries_list(self):
        """Champs à récupérer pour les sessions de communication"""
        return [
            "id",
            "login",
            "profile_name",
            "session_type",
            "start_date",
            "terminate_date",
            "connections/last/call_id",
            "connections/last/target",
            "connections/last/caller",
            "connections/last/state",
            "connections/last/create_date",
            "connections/last/terminate_date",
            "last_state_display_name",
            "last_state_date",
        ]

    def _communication_queue_xqueries_list(self):
        """Champs à récupérer pour les files de communication"""
        return [
            "id",
            "queue_name",
            "create_date",
            "terminate_date",
            "communication_type",
            "from",
            "to",
            "state",
        ]

    def _communication_task_xqueries_list(self):
        """Champs à récupérer pour les tâches de communication"""
        return [
            "id",
            "task_type",
            "create_date",
            "start_date",
            "management_effective_date",
            "end_date",
            "state",
        ]

    def on_list_response(self, view_idx, total_count, items):
        """Traiter la réponse des requêtes"""
        print(f"📊 Vue {view_idx}: {total_count} élément(s) trouvé(s)")

        try:
            # Accéder aux items via l'attribut items de consistent_protocol_list
            items_list = getattr(items, "items", [])

            if not items_list or len(items_list) == 0:
                print("   📭 Aucun élément")
                return
        except Exception as e:
            print(f"   ❌ Erreur conversion items: {e}")
            return

        # Identifier le type de vue
        view_name = "inconnue"
        if view_idx == self.communication_session_view_idx:
            view_name = "sessions"
        elif view_idx == self.communication_queue_view_idx:
            view_name = "files"
        elif view_idx == self.communication_task_view_idx:
            view_name = "tâches"

        print(f"   📋 Détails {view_name}:")

        try:
            # Essayer d'accéder aux items de différentes manières
            items_list = getattr(items, "items", items)

            # Si c'est still un objet, essayer de le convertir en liste directement
            if hasattr(items_list, "__iter__") and not isinstance(
                items_list, (list, tuple)
            ):
                items_list = list(items_list)
            elif isinstance(items_list, str):
                items_list = [items_list]
            elif not isinstance(items_list, (list, tuple)):
                print(f"   📄 Debug type: {type(items_list)}")
                print(f"   📄 Debug repr: {repr(items_list)[:200]}")
                items_list = []

            for i, item in enumerate(items_list[:5], 1):  # Limiter à 5 pour l'affichage
                self.display_item(i, item, view_name)

            if len(items_list) > 5:
                print(f"   ... et {len(items_list) - 5} autres éléments")
        except Exception as e:
            print(f"   ❌ Erreur affichage items: {e}")
            print(f"   📄 Debug items: {type(items)} - {repr(items)[:200]}")

    def display_item(self, index, item, view_type):
        """Afficher un élément de communication"""
        try:
            # L'item est un consistent_protocol_list_item avec action, item_id, rank
            item_id = getattr(item, "item_id", "N/A")
            action = getattr(item, "action", "N/A")
            rank = getattr(item, "rank", "N/A")

            print(f"      {index}. Item ID: {item_id}")
            print(f"         🔄 Action: {action}")
            print(f"         📊 Rank: {rank}")

            # Requérir l'objet complet en utilisant l'ID
            if view_type == "sessions":
                self.query_object(1, item_id, 0, "sessions")
            elif view_type == "files":
                self.query_object(2, item_id, 0, "file_tasks")
            elif view_type == "tâches":
                self.query_object(3, item_id, 0, "tasks")

            print()

        except Exception as e:
            print(f"      ❌ Erreur affichage: {e}")
            print(f"      📄 Debug: {type(item)} - {str(item)[:100]}")

    def on_object_response(self, view_idx, obj_id, obj_data):
        """Traiter la réponse d'objet"""
        print(f"         📄 Réponse objet {obj_id} pour vue {view_idx}:")
        if obj_data:
            for key, value in obj_data.items():
                if isinstance(value, dict):
                    print(f"            {key}: [objet complexe]")
                else:
                    print(f"            {key}: {value}")
        else:
            print(f"            Pas de données")

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Démarrage du monitoring des communications...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Utilisation des vues de communication CCCP")
    print("Press Ctrl+C pour arrêter\n")

    client = CommunicationMonitor("comm_monitor", DEFAULT_IP, DEFAULT_PORT)

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
