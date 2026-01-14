#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/src")
sys.path.insert(0, "/home/fblo/Documents/repos/iv-cccp/ivcommons/src")

from twisted.internet import reactor, defer
from cccp.async_module.dispatch import DispatchClient
import cccp.protocols.messages.explorer as message
from cccp.protocols.rt.lookup import IndicatorLuT


class IndicatorLister(DispatchClient):
    def __init__(self, name, ip, port):
        super(IndicatorLister, self).__init__(name, ip, port)
        self.indicator_lut = IndicatorLuT()

    def on_connection_ok(self, server_version, server_date):
        print(f"✅ Connecté au serveur CCCP {self.ip}:{self.port}")
        self.protocol.sendMessage(message.login, 1, "admin", "admin", 0, False)

    def on_login_ok(self, session_id, user_id, explorer_id):
        print(f"✅ Login OK - Session ID: {session_id}")
        self.list_all_indicators()

    def on_login_failed(self, session_id, reason):
        print(f"❌ Erreur login: {reason}")
        self.stop()

    def list_all_indicators(self):
        """Liste tous les indicateurs disponibles"""
        print("\n" + "=" * 60)
        print("📋 LISTE DES INDICATEURS DISPONIBLES")
        print("=" * 60)

        indicators = []

        # Indicateurs de base
        from cccp.protocols.rt.indicators import (
            # Session related
            SessionId,
            LastLoginDate,
            LastLogoutDate,
            StateStartDate,
            SessionCreateDate,
            SessionTerminateDate,
            # Task related
            TaskStartDate,
            TaskManagedStartDate,
            TaskManagedEndDate,
            VocalStateStartDate,
            # Communication related
            CallId,
            TaskId,
            CallStartDate,
            CallEndDate,
            CallStopWaitingDate,
            CallManagementDate,
            CallPostManagementDate,
            LocalNumber,
            RemoteNumber,
            SessionType,
            # Advanced indicators
            CommunicationId,
            CommunicationTaskId,
            CallIdentifier,
            CreateDate,
            StartDate,
            EndDate,
            CommunicationCreateDate,
        )

        # Créer instances et collecter les noms
        all_classes = [
            SessionId,
            LastLoginDate,
            LastLogoutDate,
            StateStartDate,
            SessionCreateDate,
            SessionTerminateDate,
            TaskStartDate,
            TaskManagedStartDate,
            TaskManagedEndDate,
            VocalStateStartDate,
            CallId,
            TaskId,
            CallStartDate,
            CallEndDate,
            CallStopWaitingDate,
            CallManagementDate,
            CallPostManagementDate,
            LocalNumber,
            RemoteNumber,
            SessionType,
            CommunicationId,
            CommunicationTaskId,
            CallIdentifier,
            CreateDate,
            StartDate,
            EndDate,
            CommunicationCreateDate,
        ]

        for cls in all_classes:
            try:
                instance = cls()
                indicators.append(instance.name)
            except Exception as e:
                print(f"Erreur avec {cls.__name__}: {e}")

        print(f"📊 Total: {len(indicators)} indicateurs")
        print()

        # Regrouper par type
        print("📞 INDICATEURS DE COMMUNICATION:")
        comm_indicators = [
            i
            for i in indicators
            if any(
                word in i.lower()
                for word in ["call", "communication", "task", "local", "remote"]
            )
        ]
        for indicator in sorted(comm_indicators):
            print(f"  - {indicator}")

        print()
        print("📅 INDICATEURS DE SESSION:")
        session_indicators = [
            i
            for i in indicators
            if any(word in i.lower() for word in ["session", "login", "logout"])
        ]
        for indicator in sorted(session_indicators):
            print(f"  - {indicator}")

        print()
        print("🕐 INDICATEURS D'ÉTAT:")
        state_indicators = [
            i for i in indicators if "state" in i.lower() or "vocal" in i.lower()
        ]
        for indicator in sorted(state_indicators):
            print(f"  - {indicator}")

        print()
        print("📅 INDICATEURS DE DATE:")
        date_indicators = [
            i
            for i in indicators
            if "date" in i.lower()
            or "start" in i.lower()
            or "end" in i.lower()
            or "create" in i.lower()
        ]
        for indicator in sorted(date_indicators):
            print(f"  - {indicator}")

        print("\n" + "=" * 60)

        # Tenter de créer un listener de communication
        try:
            comm_listener = self.indicator_lut.get_communication_listener()
            if comm_listener:
                print("✅ CommunicationListener disponible")

                # Essayer de récupérer les communications actives
                print("📊 Tentative de récupération des communications...")
                try:
                    values = comm_listener.get_values(
                        [
                            "communication_id",
                            "session_type",
                            "session_id",
                            "terminate_date",
                            "user_login",
                            "local_number",
                            "remote_number",
                            "start_date",
                            "create_date",
                        ]
                    )
                    print(f"   Résultat: {len(values)} communication(s) trouvée(s)")

                    if values:
                        print("   Communications actives:")
                        for i, comm in enumerate(values[:5], 1):
                            print(f"     {i}. {comm}")

                except Exception as e:
                    print(f"   ❌ Erreur récupération: {e}")
            else:
                print("❌ CommunicationListener non disponible")

        except Exception as e:
            print(f"❌ Erreur CommunicationListener: {e}")

        print("\n👋 Arrêt du listing")
        self.stop()


def main():
    DEFAULT_IP = "10.199.30.67"
    DEFAULT_PORT = 20103

    print("🔍 Listing des indicateurs CCCP...")
    print(f"🌐 Serveur: {DEFAULT_IP}:{DEFAULT_PORT}\n")

    client = IndicatorLister("indicator_lister", DEFAULT_IP, DEFAULT_PORT)

    try:
        client.connect()
        reactor.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé")
        client.stop()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
