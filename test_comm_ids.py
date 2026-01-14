#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message


class SimpleCommMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(SimpleCommMonitor, self).__init__(name, ip, port)
        self.communication_ids = set()

    def connect_done(self, result_value):
        """Configuration simple pour voir les IDs de communication"""
        print("🔧 Configuration du monitoring des communications...")

        # Créer une vue simple pour les sessions avec communications
        self.communication_session_view_idx = self.start_view(
            "sessions",
            "communications_sessions",
            self._simple_xqueries_list,
            ".[connections/last/call_id ne '' and session_type ne 3]",
        )

        print(f"✅ Vue créée: {self.communication_session_view_idx}")

        # Démarrer le monitoring après 2 secondes
        reactor.callLater(2, self.start_monitoring)

    def _simple_xqueries_list(self):
        """Champs simples à récupérer"""
        return [
            "id",
            "login",
            "profile_name",
            "session_type",
            "connections/last/call_id",
            "connections/last/target",
            "connections/last/caller",
            "connections/last/state",
        ]

    def start_monitoring(self):
        print("📞 Démarrage monitoring...")
        reactor.callLater(0, self.monitor_loop)

    def monitor_loop(self):
        print(f"\n{'=' * 50}")
        print(f"📞 SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)

        try:
            # Lancer la requête sur la vue des communications
            if self.communication_session_view_idx:
                print("🔍 Recherche des communications...")
                self.query_list(
                    self.communication_session_view_idx,
                    "sessions",
                    ".[connections/last/call_id ne '' and session_type ne 3]",
                )

        except Exception as e:
            print(f"❌ Erreur: {e}")

        # Continuer le monitoring
        reactor.callLater(5, self.monitor_loop)

    def on_list_response(self, view_idx, total_count, items):
        """Traiter la réponse des requêtes"""
        print(f"📊 Vue {view_idx}: {total_count} communication(s) trouvée(s)")

        try:
            # Accéder aux items
            items_list = getattr(items, "items", [])

            if not items_list or len(items_list) == 0:
                print("   📭 Aucune communication")
                return

            print(f"   📋 Communications actives:")
            new_communications = set()

            for item in items_list:
                item_id = getattr(item, "item_id", "N/A")
                action = getattr(item, "action", "N/A")
                rank = getattr(item, "rank", "N/A")

                new_communications.add(item_id)

                # Déterminer si c'est nouveau
                if item_id not in self.communication_ids:
                    print(
                        f"      🆕 NOUVEAU: ID={item_id}, Action={action}, Rank={rank}"
                    )
                    self.communication_ids.add(item_id)
                else:
                    print(f"      📞 ID={item_id}, Action={action}, Rank={rank}")

            # Afficher le résumé
            print(f"   📈 Total communications actives: {len(self.communication_ids)}")

            if len(new_communications) > len(self.communication_ids):
                print(
                    f"   ✨ {len(new_communications) - len(self.communication_ids)} nouvelle(s) communication(s)"
                )

        except Exception as e:
            print(f"   ❌ Erreur traitement: {e}")

    def stop(self):
        print("\n👋 Arrêt du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🚀 Monitoring SIMPLE des communications...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("📞 Affichage des IDs de communication actifs")
    print("Press Ctrl+C pour arrêter\n")

    client = SimpleCommMonitor("simple_monitor", DEFAULT_IP, DEFAULT_PORT)

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
