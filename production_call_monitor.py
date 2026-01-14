#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class ProductionCallMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(ProductionCallMonitor, self).__init__(name, ip, port)
        self.cycle_count = 0
        self.communication_session_view_idx = None
        self.communication_queue_view_idx = None
        self.communication_task_view_idx = None
        self.known_communications = {}
        self.communication_details = {}

    def connect_done(self, result_value):
        """Configuration des vues de communication complètes"""
        print("🔧 Configuration du système de monitoring des appels...")

        # Vue pour les sessions de communication (appels en cours)
        self.communication_session_view_idx = self.start_view(
            "sessions",
            "communications_sessions",
            self._session_xqueries_list,
            ".[connections/last/call_id ne '' and (session_type eq 1 or session_type eq 2 or session_type eq 4)]",
        )

        # Vue pour les files d'attente (appels en file)
        self.communication_queue_view_idx = self.start_view(
            "file_tasks",
            "communications_queues",
            self._queue_xqueries_list,
            ".[terminate_date eq '' and task_type eq 'assigning']",
        )

        # Vue pour les tâches de communication
        self.communication_task_view_idx = self.start_view(
            "tasks",
            "communications_tasks",
            self._task_xqueries_list,
            ".[task_type eq 'assigning' or task_type eq 'processing']",
        )

        print(f"✅ Vues configurées:")
        print(f"   📞 Sessions: {self.communication_session_view_idx}")
        print(f"   📋 Files: {self.communication_queue_view_idx}")
        print(f"   🔧 Tâches: {self.communication_task_view_idx}")

        # Démarrer le monitoring après 3 secondes
        reactor.callLater(3, self.start_production_monitoring)

    def _session_xqueries_list(self):
        """Champs pour les sessions (appels actifs)"""
        return [
            "id",
            "login",
            "profile_name",
            "session_type",
            "start_date",
            "terminate_date",
            "last_state_display_name",
            "last_state_date",
            "connections/last/call_id",
            "connections/last/target",
            "connections/last/caller",
            "connections/last/state",
            "connections/last/create_date",
            "connections/last/terminate_date",
            "connections/last/hold_flag",
            "attributes/remote_number/value",
            "attributes/local_number/value",
        ]

    def _queue_xqueries_list(self):
        """Champs pour les files d'attente"""
        return [
            "id",
            "queue_name",
            "task_type",
            "create_date",
            "terminate_date",
            "start_date",
            "management_effective_date",
            "state",
            "priority",
            "from",
            "to",
            "caller",
            "called",
        ]

    def _task_xqueries_list(self):
        """Champs pour les tâches"""
        return [
            "id",
            "task_type",
            "create_date",
            "start_date",
            "management_effective_date",
            "end_date",
            "state",
            "priority",
            "queue_name",
            "manager_session/user/login",
        ]

    def start_production_monitoring(self):
        print("🚀 DÉMARRAGE DU MONITORING DE PRODUCTION")
        print("📞 Surveillance des appels en temps réel...")
        reactor.callLater(0, self.production_monitor_loop)

    def production_monitor_loop(self):
        self.cycle_count += 1
        print(f"\n{'=' * 80}")
        print(
            f"📞 CYCLE DE MONITORING {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}"
        )
        print("=" * 80)

        try:
            # Scanner toutes les vues
            if self.communication_session_view_idx:
                print("📡 Scan des sessions d'appels actives...")
                self.query_list(
                    self.communication_session_view_idx,
                    "sessions",
                    ".[connections/last/call_id ne '' and (session_type eq 1 or session_type eq 2 or session_type eq 4)]",
                )

            if self.communication_queue_view_idx:
                print("📋 Scan des files d'attente...")
                self.query_list(
                    self.communication_queue_view_idx,
                    "file_tasks",
                    ".[terminate_date eq '' and task_type eq 'assigning']",
                )

            if self.communication_task_view_idx:
                print("🔧 Scan des tâches de communication...")
                self.query_list(
                    self.communication_task_view_idx,
                    "tasks",
                    ".[task_type eq 'assigning' or task_type eq 'processing']",
                )

        except Exception as e:
            print(f"❌ Erreur during monitoring: {e}")
            import traceback

            traceback.print_exc()

        # Continuer le monitoring toutes les 15 secondes
        reactor.callLater(15, self.production_monitor_loop)

    def on_list_response(self, view_idx, total_count, items):
        """Traiter les réponses de monitoring"""
        view_name = self.get_view_name(view_idx)
        print(f"\n📊 {view_name}: {total_count} élément(s) trouvé(s)")

        try:
            items_list = getattr(items, "items", [])

            if not items_list or len(items_list) == 0:
                print(f"   📭 Aucun élément dans {view_name}")
                if view_name == "SESSIONS":
                    print("   🎯 Aucun appel actif en ce moment")
                return

            print(f"   📋 Détails {view_name}:")

            # Traiter chaque item et requérir les détails complets
            for item in items_list:
                item_id = getattr(item, "item_id", "N/A")
                action = getattr(item, "action", "N/A")
                rank = getattr(item, "rank", "N/A")

                # Stocker pour tracking
                self.known_communications[item_id] = {
                    "view": view_name,
                    "action": action,
                    "rank": rank,
                    "last_seen": datetime.now(),
                }

                # Requérir l'objet complet
                self.query_object(view_idx, item_id, 0, self.get_view_root(view_name))

        except Exception as e:
            print(f"   ❌ Erreur traitement {view_name}: {e}")

    def on_object_response(self, view_idx, obj_id, obj_data):
        """Traiter les objets complets"""
        view_name = self.get_view_name(view_idx)

        if obj_data:
            self.communication_details[obj_id] = obj_data
            self.display_communication_details(obj_id, obj_data, view_name)
        else:
            print(f"   ⚠️  Pas de données pour l'objet {obj_id}")

    def get_view_name(self, view_idx):
        """Obtenir le nom lisible de la vue"""
        if view_idx == self.communication_session_view_idx:
            return "SESSIONS"
        elif view_idx == self.communication_queue_view_idx:
            return "FILES"
        elif view_idx == self.communication_task_view_idx:
            return "TÂCHES"
        else:
            return f"VUE_{view_idx}"

    def get_view_root(self, view_idx):
        """Obtenir le root de la vue pour les requêtes d'objets"""
        view_name = self.get_view_name(view_idx)
        if view_name == "SESSIONS":
            return "sessions"
        elif view_name == "FILES":
            return "file_tasks"
        elif view_name == "TÂCHES":
            return "tasks"
        else:
            return "sessions"

    def display_communication_details(self, obj_id, obj_data, view_name):
        """Afficher les détails complets d'une communication"""
        try:
            print(f"\n   📞 DÉTAILS DE COMMUNICATION #{obj_id} ({view_name})")
            print("   " + "─" * 60)

            if view_name == "SESSIONS":
                self.display_session_details(obj_data)
            elif view_name == "FILES":
                self.display_queue_details(obj_data)
            elif view_name == "TÂCHES":
                self.display_task_details(obj_data)

        except Exception as e:
            print(f"   ❌ Erreur affichage détails {obj_id}: {e}")
            print(f"   📄 Debug: {str(obj_data)[:200]}")

    def display_session_details(self, data):
        """Afficher les détails d'une session (appel actif)"""
        # Informations générales
        session_id = data.get("id", "N/A")
        login = data.get("login", "N/A")
        profile = data.get("profile_name", "N/A")
        session_type = data.get("session_type", "N/A")

        # État
        state = data.get("last_state_display_name", "N/A")
        state_date = data.get("last_state_date", "")
        terminate_date = data.get("terminate_date", "")

        # Connexion
        call_id = data.get("connections/last/call_id", "")
        target = data.get("connections/last/target", "")
        caller = data.get("connections/last/caller", "")
        conn_state = data.get("connections/last/state", "")
        hold_flag = data.get("connections/last/hold_flag", False)

        # Numéros
        local_num = data.get("attributes/local_number/value", "")
        remote_num = data.get("attributes/remote_number/value", "")

        # Dates
        start_date = data.get("start_date", "")
        conn_create_date = data.get("connections/last/create_date", "")

        # Déterminer le statut
        if terminate_date:
            status = "🔴 TERMINÉ"
        elif hold_flag:
            status = "⏸️ EN ATTENTE"
        elif conn_state == "processing":
            status = "📞 EN COMMUNICATION"
        elif conn_state == "ringing":
            status = "🔔 EN SONNERIE"
        else:
            status = "🟡 ACTIF"

        # Nettoyer les numéros
        if local_num and local_num.startswith("tel:"):
            local_num = local_num[4:]
        if remote_num and remote_num.startswith("tel:"):
            remote_num = remote_num[4:]
        if target and target.startswith("tel:"):
            target = target[4:]
        if caller and caller.startswith("tel:"):
            caller = caller[4:]

        print(f"      📊 {status} | Utilisateur: {login}")
        print(f"      👤 Profile: {profile} | Type: {session_type}")
        print(f"      📋 Session ID: {session_id}")
        print(f"      📞 Call ID: {call_id}")
        print(f"      📱 Poste: {local_num or target or 'N/A'}")
        print(f"      📝 Appelant: {caller or remote_num or 'N/A'}")
        print(f"      🔄 État connexion: {conn_state}")
        print(f"      📊 État session: {state}")
        print(f"      ⏰️ Début: {start_date or conn_create_date}")
        if terminate_date:
            print(f"      🕐 Fin: {terminate_date}")

    def display_queue_details(self, data):
        """Afficher les détails d'une file d'attente"""
        task_id = data.get("id", "N/A")
        queue_name = data.get("queue_name", "N/A")
        task_type = data.get("task_type", "N/A")
        state = data.get("state", "N/A")
        priority = data.get("priority", "N/A")

        caller = data.get("caller", "")
        called = data.get("called", "")
        from_field = data.get("from", "")
        to_field = data.get("to", "")

        create_date = data.get("create_date", "")
        start_date = data.get("start_date", "")

        print(f"      📋 Tâche en file: {task_id}")
        print(f"      📞 File d'attente: {queue_name}")
        print(f"      🔧 Type: {task_type}")
        print(f"      🔄 État: {state}")
        print(f"      ⭐ Priorité: {priority}")
        print(f"      📱 Appelant: {caller or from_field or 'N/A'}")
        print(f"      📝 Appelé: {called or to_field or 'N/A'}")
        print(f"      ⏰️ Création: {create_date}")
        if start_date:
            print(f"      🎯 Début traitement: {start_date}")

    def display_task_details(self, data):
        """Afficher les détails d'une tâche"""
        task_id = data.get("id", "N/A")
        task_type = data.get("task_type", "N/A")
        state = data.get("state", "N/A")
        queue_name = data.get("queue_name", "N/A")
        manager = data.get("manager_session/user/login", "N/A")

        priority = data.get("priority", "N/A")
        create_date = data.get("create_date", "")
        start_date = data.get("start_date", "")
        mgmt_date = data.get("management_effective_date", "")
        end_date = data.get("end_date", "")

        print(f"      🔧 Tâche: {task_id}")
        print(f"      📊 Type: {task_type}")
        print(f"      🔄 État: {state}")
        print(f"      📞 File: {queue_name}")
        print(f"      👤 Géré par: {manager}")
        print(f"      ⭐ Priorité: {priority}")
        print(f"      ⏰️ Création: {create_date}")
        if start_date:
            print(f"      🎯 Début: {start_date}")
        if mgmt_date:
            print(f"      ✅ Prise en charge: {mgmt_date}")
        if end_date:
            print(f"      🕐 Fin: {end_date}")

    def stop(self):
        print("\n👋 Arrêt du monitoring de production")
        print(f"📊 Résumé: {len(self.communication_details)} communications monitorées")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 SYSTÈME DE MONITORING D'APPELS - VERSION PRODUCTION")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Monitoring temps réel des appels CCCP")
    print("🔍 Sessions, Files d'attente, Tâches")
    print("Press Ctrl+C pour arrêter\n")

    client = ProductionCallMonitor("prod_call_monitor", DEFAULT_IP, DEFAULT_PORT)

    try:
        client.connect()
        reactor.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé par l'utilisateur")
        client.stop()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
