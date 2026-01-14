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


class QuickCallMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(QuickCallMonitor, self).__init__(name, ip, port)
        self.communication_session_view_idx = None
        self.communication_queue_view_idx = None
        self.cycle_count = 0

    def connect_done(self, result_value):
        """Configuration rapide des vues"""
        print("🔧 Configuration des vues de monitoring...")

        # Vue pour les sessions de communication (appels actifs)
        self.communication_session_view_idx = self.start_view(
            "sessions",
            "calls_active",
            self._essential_session_fields,
            ".[connections/last/call_id ne '' and session_type ne 3]",
        )

        # Vue pour les files d'attente
        self.communication_queue_view_idx = self.start_view(
            "file_tasks",
            "calls_waiting",
            self._essential_queue_fields,
            ".[terminate_date eq '' and task_type eq 'assigning']",
        )

        print(
            f"✅ Vues créées - Sessions: {self.communication_session_view_idx}, Files: {self.communication_queue_view_idx}"
        )

        # Démarrer immédiatement
        reactor.callLater(1, self.start_monitoring)

    def _essential_session_fields(self):
        """Champs essentiels pour les sessions d'appels"""
        return [
            "id",
            "login",
            "profile_name",
            "session_type",
            "start_date",
            "terminate_date",
            "last_state_display_name",
            "connections/last/call_id",
            "connections/last/target",
            "connections/last/caller",
            "connections/last/state",
            "attributes/remote_number/value",
            "attributes/local_number/value",
        ]

    def _essential_queue_fields(self):
        """Champs essentiels pour les files d'attente"""
        return [
            "id",
            "queue_name",
            "task_type",
            "create_date",
            "terminate_date",
            "state",
            "from",
            "to",
            "caller",
            "called",
        ]

    def start_monitoring(self):
        print("🚀 DÉMARRAGE IMMÉDIAT DU MONITORING")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        self.cycle_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n{'=' * 70}")
        print(f"📞 SCAN {self.cycle_count} - {timestamp}")
        print("=" * 70)

        try:
            # Scanner les sessions d'appels
            if self.communication_session_view_idx:
                print("🔍 Scan des appels actifs...")
                self.query_list(
                    self.communication_session_view_idx,
                    "sessions",
                    ".[connections/last/call_id ne '' and session_type ne 3]",
                )

            # Scanner les files d'attente
            if self.communication_queue_view_idx:
                print("📋 Scan des appels en attente...")
                self.query_list(
                    self.communication_queue_view_idx,
                    "file_tasks",
                    ".[terminate_date eq '' and task_type eq 'assigning']",
                )

        except Exception as e:
            print(f"❌ Erreur: {e}")

        # Continuer toutes les 10 secondes
        reactor.callLater(10, self.monitor_loop)

    def on_list_response(self, view_idx, total_count, items):
        """Traiter et afficher les communications"""
        view_name = (
            "APPELS ACTIFS"
            if view_idx == self.communication_session_view_idx
            else "APPELS EN ATTENTE"
        )

        print(f"\n📊 {view_name}: {total_count} trouvé(s)")

        try:
            items_list = getattr(items, "items", [])

            if not items_list or len(items_list) == 0:
                print(f"   📭 Aucun {view_name.lower()}")
                return

            # Afficher le résumé
            active_count = len(items_list)
            print(f"   📈 Total: {active_count} {view_name.lower()}")

            # Traiter chaque item
            for i, item in enumerate(
                items_list[:10], 1
            ):  # Limiter à 10 pour la lisibilité
                item_id = getattr(item, "item_id", "N/A")
                action = getattr(item, "action", "N/A")
                rank = getattr(item, "rank", "N/A")

                print(
                    f"\n      {i}. 🆔 ID: {item_id} | Action: {action} | Rang: {rank}"
                )

                # Requérir les détails complets de l'objet
                if view_idx == self.communication_session_view_idx:
                    self.query_object(view_idx, item_id, 0, "sessions")
                else:
                    self.query_object(view_idx, item_id, 0, "file_tasks")

            if len(items_list) > 10:
                print(
                    f"\n      ... et {len(items_list) - 10} autres {view_name.lower()}"
                )

        except Exception as e:
            print(f"   ❌ Erreur traitement: {e}")

    def on_object_response(self, view_idx, obj_id, obj_data):
        """Afficher les détails complets d'un objet"""
        view_name = (
            "APPEL ACTIF"
            if view_idx == self.communication_session_view_idx
            else "APPEL EN ATTENTE"
        )

        if not obj_data:
            print(f"      ⚠️  Pas de détails pour {obj_id}")
            return

        print(f"      📋 Détails {view_name} #{obj_id}:")

        try:
            if view_idx == self.communication_session_view_idx:
                self.display_call_details(obj_data)
            else:
                self.display_waiting_call_details(obj_data)

        except Exception as e:
            print(f"      ❌ Erreur affichage: {e}")

    def display_call_details(self, data):
        """Afficher les détails d'un appel actif"""
        # Infos utilisateur
        login = data.get("login", "N/A")
        profile = data.get("profile_name", "N/A")

        # Connexion
        call_id = data.get("connections/last/call_id", "")
        target = data.get("connections/last/target", "")
        caller = data.get("connections/last/caller", "")
        conn_state = data.get("connections/last/state", "N/A")

        # Numéros
        local_num = data.get("attributes/local_number/value", "")
        remote_num = data.get("attributes/remote_number/value", "")

        # État
        state = data.get("last_state_display_name", "N/A")
        terminate_date = data.get("terminate_date", "")

        # Statut visuel
        if terminate_date:
            status = "🔴 TERMINÉ"
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

        print(f"         📊 {status}")
        print(f"         👤 Utilisateur: {login} (Profile: {profile})")
        print(f"         📞 Call ID: {call_id}")
        print(f"         📱 Poste: {local_num or target or 'N/A'}")
        print(f"         📝 Appelant: {caller or remote_num or 'N/A'}")
        print(f"         🔄 État: {conn_state} | {state}")

    def display_waiting_call_details(self, data):
        """Afficher les détails d'un appel en attente"""
        task_id = data.get("id", "N/A")
        queue_name = data.get("queue_name", "N/A")
        state = data.get("state", "N/A")

        caller = data.get("caller", "")
        called = data.get("called", "")
        from_field = data.get("from", "")
        to_field = data.get("to", "")

        create_date = data.get("create_date", "")

        print(f"         📋 File d'attente: {queue_name}")
        print(f"         🆔 Tâche: {task_id}")
        print(f"         🔄 État: {state}")
        print(f"         📱 Appelant: {caller or from_field or 'N/A'}")
        print(f"         📝 Appelé: {called or to_field or 'N/A'}")
        print(f"         ⏰️ En attente depuis: {create_date}")

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 MONITORING RAPIDE DES APPELS CCCP")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Scan temps réel des appels actifs et en attente")
    print("Press Ctrl+C pour arrêter\n")

    client = QuickCallMonitor("quick_monitor", DEFAULT_IP, DEFAULT_PORT)

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
