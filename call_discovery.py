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


class CallDiscoveryMonitor(DispatchClient):
    def __init__(self, name, ip, port):
        super(CallDiscoveryMonitor, self).__init__(name, ip, port)
        self.communication_view_idx = None
        self.discovered_calls = set()

    def connect_done(self, result_value):
        """Configuration pour découvrir les appels"""
        print("🔧 Configuration de la découverte d'appels...")

        # Vue simple pour détecter les communications
        self.communication_view_idx = self.start_view(
            "sessions",
            "call_discovery",
            self._minimal_fields,
            ".[connections/last/call_id ne '']",
        )

        print(f"✅ Vue de découverte créée: {self.communication_view_idx}")

        # Démarrer rapidement
        reactor.callLater(1, self.discover_calls)

    def _minimal_fields(self):
        """Champs minimaux pour détecter les appels"""
        return ["id", "connections/last/call_id", "connections/last/state"]

    def discover_calls(self):
        print("🔍 DÉCOUVERTE DES APPELS...")

        try:
            if self.communication_view_idx:
                print("📞 Recherche des appels...")
                self.query_list(
                    self.communication_view_idx,
                    "sessions",
                    ".[connections/last/call_id ne '']",
                )

        except Exception as e:
            print(f"❌ Erreur découverte: {e}")

    def on_list_response(self, view_idx, total_count, items):
        """Traiter les appels découverts"""
        print(f"\n📊 RÉSULTAT: {total_count} communication(s) avec call_id trouvé(s)")

        try:
            items_list = getattr(items, "items", [])

            if not items_list or len(items_list) == 0:
                print("   📭 Aucun appel avec call_id trouvé")
                return

            print(f"\n📋 APPELS DÉCOUVERTS:")
            print("=" * 60)

            new_calls = set()

            for i, item in enumerate(items_list, 1):
                item_id = getattr(item, "item_id", "N/A")
                action = getattr(item, "action", "N/A")
                rank = getattr(item, "rank", "N/A")

                new_calls.add(item_id)

                # Nouveau ou connu
                status = (
                    "🆕 NOUVEAU" if item_id not in self.discovered_calls else "📞 CONNU"
                )

                print(f"{i}. {status} - Session ID: {item_id}")
                print(f"   🔄 Action: {action} | Rang: {rank}")

                if item_id not in self.discovered_calls:
                    self.discovered_calls.add(item_id)
                    print(f"   ✨ Premier scan de cet appel!")

                # Requérir les détails de base
                self.query_object(view_idx, item_id, 0, "sessions")

            print("=" * 60)
            print(f"📊 Résumé: {len(new_calls)} appel(s) dans ce scan")
            print(f"📈 Total unique découvert: {len(self.discovered_calls)} appel(s)")

            if len(new_calls) > len(self.discovered_calls):
                newly_discovered = len(new_calls) - len(self.discovered_calls)
                print(f"🎉 {newly_discovered} nouvel(s) appel(s) découvert(s)!")

        except Exception as e:
            print(f"   ❌ Erreur traitement: {e}")

    def on_object_response(self, view_idx, obj_id, obj_data):
        """Afficher les détails de l'objet"""
        if obj_data:
            print(f"\n   📋 DÉTAILS SESSION #{obj_id}:")

            # Informations essentielles
            login = obj_data.get("login", "N/A")
            profile = obj_data.get("profile_name", "N/A")
            session_type = obj_data.get("session_type", "N/A")

            # Connexion
            call_id = obj_data.get("connections/last/call_id", "")
            conn_state = obj_data.get("connections/last/state", "N/A")
            target = obj_data.get("connections/last/target", "")
            caller = obj_data.get("connections/last/caller", "")

            # État
            state = obj_data.get("last_state_display_name", "N/A")
            start_date = obj_data.get("start_date", "")
            terminate_date = obj_data.get("terminate_date", "")

            # Numéros
            local_num = obj_data.get("attributes/local_number/value", "")
            remote_num = obj_data.get("attributes/remote_number/value", "")

            # Nettoyer les numéros
            if local_num and local_num.startswith("tel:"):
                local_num = local_num[4:]
            if remote_num and remote_num.startswith("tel:"):
                remote_num = remote_num[4:]
            if target and target.startswith("tel:"):
                target = target[4:]
            if caller and caller.startswith("tel:"):
                caller = caller[4:]

            # Statut
            if terminate_date:
                status = "🔴 TERMINÉ"
            elif conn_state == "processing":
                status = "📞 EN COURS"
            elif conn_state == "ringing":
                status = "🔔 SONNERIE"
            else:
                status = "🟡 ACTIF"

            print(f"      📊 {status}")
            print(f"      👤 Utilisateur: {login} (Profile: {profile})")
            print(f"      📞 Call ID: {call_id}")
            print(f"      📊 Type session: {session_type}")
            print(f"      📱 Poste: {local_num or target or 'N/A'}")
            print(f"      📝 Appelant: {caller or remote_num or 'N/A'}")
            print(f"      🔄 État connexion: {conn_state}")
            print(f"      📋 État session: {state}")
            print(f"      ⏰️ Début: {start_date}")
            if terminate_date:
                print(f"      🕐 Fin: {terminate_date}")
        else:
            print(f"   ⚠️  Pas de détails pour session #{obj_id}")

    def stop(self):
        print(f"\n🎯 DÉCOUVERTE TERMINÉE")
        print(f"📊 Total unique d'appels découverts: {len(self.discovered_calls)}")
        print("👋 Fin du monitoring")
        if reactor.running:
            reactor.stop()
        sys.exit(0)


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🎯 SYSTÈME DE DÉCOUVERTE D'APPELS")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}")
    print("🔍 Scan unique pour découvrir tous les appels")
    print("📞 Sessions avec call_id uniquement")
    print("\nPress Ctrl+C pour arrêter\n")

    client = CallDiscoveryMonitor("call_discovery", DEFAULT_IP, DEFAULT_PORT)

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
