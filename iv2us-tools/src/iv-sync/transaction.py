#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's IV2US Tools.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>
#    - SLAU <slau@interact-iv.com>
#    - GRIC <gric@interact-iv.com>

from __future__ import division, print_function
from collections import OrderedDict

from ivsync.checks import VERIFY_RANGE
from ivsync.webadminobjects import WARNS
from ivsync.collectionobjects import ERRORS

from trest import TrestNoContent

from twisted.internet import reactor, stdio
from twisted.internet import defer
from twisted.protocols import basic
from twisted.python import log


class Transaction(object):
    def __init__(self, configapi_client, webadmin_client):
        self._client = configapi_client
        self._db_client = webadmin_client
        self._whitelabels = []
        self._projects = {}
        self._agents_folders = {}
        self._supervisors_folders = {}
        self._agents = {}
        self._supervisors = {}
        self._profiles = {}
        self._vocal_queues = {}
        self._mail_queues = {}
        self._transfer_targets_folders = {}
        self._transfer_targets = {}
        self._profiles_folders = {}
        self._queues_folders = {}
        self._positions_folders = {}
        self._positions = {}
        self._calendars = {}
        self._specialdays = {}
        self._scenarios = {}
        self._scenarios_folders = {}
        self._entrypoints = {}
        self._soundfiles_folders = {}
        self._soundfiles = {}

        self._profile_updates = []
        self._agents_folder_updates = []
        self._supervisors_folder_updates = []
        self._agent_updates = []
        self._supervisor_updates = []
        self._vocal_queue_updates = []
        self._mail_queue_updates = []
        self._transfer_targets_folder_updates = []
        self._transfer_target_updates = []
        self._profiles_folder_updates = []
        self._queues_folder_updates = []
        self._positions_folder_updates = []
        self._position_updates = []
        self._scenarios_folder_updates = []

        self.create_map = {
            'agents': self._agents,
            'supervisors': self._supervisors,
            'profiles': self._profiles,
            'vocal_queues': self._vocal_queues,
            'mail_queues': self._mail_queues,
            'transfer_targets_folders': self._transfer_targets_folders,
            'transfer_targets': self._transfer_targets,
            'profiles_folders': self._profiles_folders,
            'queues_folders': self._queues_folders,
            'positions_folders': self._positions_folders,
            'positions': self._positions,
            'agents_folders': self._agents_folders,
            'supervisors_folders': self._supervisors_folders,
            'calendars': self._calendars,
            'specialdays': self._specialdays,
            'scenarios': self._scenarios,
            'scenarios_folders': self._scenarios_folders,
            'entrypoints': self._entrypoints,
            'soundfilesfolders': self._soundfiles_folders,
            'soundfiles': self._soundfiles,
        }

        self.update_map = {
            'agents': self._agent_updates,
            'supervisors': self._supervisor_updates,
            'profiles': self._profile_updates,
            'vocal_queues': self._vocal_queue_updates,
            'mail_queues': self._mail_queue_updates,
            'transfer_targets_folders': self._transfer_targets_folder_updates,
            'transfer_targets': self._transfer_target_updates,
            'profiles_folders': self._profiles_folder_updates,
            'queues_folders': self._queues_folder_updates,
            'positions_folders': self._positions_folder_updates,
            'positions': self._position_updates,
            'agents_folders': self._agents_folder_updates,
            'supervisors_folders': self._supervisors_folder_updates,
            'scenarios_folders': self._scenarios_folder_updates,
        }

    def create_whitelabel(self, whitelabel):
        if whitelabel not in self._whitelabels:
            log.msg("%s needs to be created." % (whitelabel,))
            self._whitelabels.append(whitelabel)

    def create_project(self, project):
        if project._whitelabel not in self._projects:
            self._projects[project._whitelabel] = []

        if project not in self._projects[project._whitelabel]:
            log.msg("%s needs to be created." % (project,))
            self._projects[project._whitelabel].append(project)

    def create_ressource(self, ressource, ressource_type):
        _map = self.create_map[ressource_type]
        wl = ressource._whitelabel
        prj = ressource._project

        if wl not in _map:
            _map[wl] = {}

        if ressource._project not in _map[wl]:
            _map[wl][prj] = []

        if ressource not in _map[wl][prj]:
            log.msg("%s need to be created." % (ressource,))
            _map[wl][prj].append(ressource)

    def update_ressource(self, ressource_type, webadmin_ressource, api_ressource):
        log.msg("%s needs to be updated." % (webadmin_ressource,))
        self.update_map[ressource_type].append((webadmin_ressource, api_ressource))

    def print_results(self, _, quiet, has_calendars, has_soundfilesfolders, api_only):
        prompt = Prompt("The following actions need to be completed:")
        stdio.StandardIO(prompt)

        if len(self._whitelabels):
            wl_names = ', '.join([x.name for x in self._whitelabels])
            prompt.sendLine("- Create whitelabels: %s" % (wl_names,))

        for wl in self._projects:
            prj_names = ', '.join([x.name for x in self._projects[wl]])
            prompt.sendLine("- [Whitelabel %s] Create projects: %s" % (
                wl, prj_names))

        for wl in self._profiles:
            for prj in self._profiles[wl]:
                profile_names = ', '.join(
                    [x.name for x in self._profiles[wl][prj]])
                prompt.sendLine("- [Project %s:%s] Create profiles: %s" % (
                    wl, prj, profile_names))

        for webadmin_profile, _ in self._profile_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_profile,))

        for wl in self._agents_folders:
            for prj in self._agents_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create agents folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._agents_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_agents_folder, _ in \
                self._agents_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_agents_folder,))

        for wl in self._supervisors_folders:
            for prj in self._supervisors_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create supervisors folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._supervisors_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_supervisors_folder, _ in \
                self._supervisors_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_supervisors_folder,))

        for wl in self._agents:
            for prj in self._agents[wl]:
                agent_names = ', '.join(
                    [x.name for x in self._agents[wl][prj]])
                prompt.sendLine("- [Project %s:%s] Create agents: %s" % (
                    wl, prj, agent_names))

        for webadmin_agent, _ in self._agent_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_agent,))

        for wl in self._supervisors:
            for prj in self._supervisors[wl]:
                supervisor_names = ', '.join(
                    [x.name for x in self._supervisors[wl][prj]])
                prompt.sendLine("- [Project %s:%s] Create supervisors: %s" % (
                    wl, prj, supervisor_names))

        for webadmin_supervisor, _ in self._supervisor_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_supervisor,))

        for wl in self._vocal_queues:
            for prj in self._vocal_queues[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create vocal queues: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._vocal_queues[wl][prj]]
                        )
                    )
                )

        for webadmin_vocal_queue, _ in \
                self._vocal_queue_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_vocal_queue,))

        for wl in self._mail_queues:
            for prj in self._mail_queues[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create mail queues: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._mail_queues[wl][prj]]
                        )
                    )
                )

        for webadmin_mail_queue, _ in self._mail_queue_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_mail_queue,))

        for wl in self._transfer_targets_folders:
            for prj in self._transfer_targets_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create transfer targets folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._transfer_targets_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_transfer_targets_folder, _ in self._transfer_targets_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_transfer_targets_folder,))

        for wl in self._transfer_targets:
            for prj in self._transfer_targets[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create transfer targets: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._transfer_targets[wl][prj]]
                        )
                    )
                )

        for webadmin_transfer_targets, _ in self._transfer_target_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_transfer_targets,))

        for wl in self._profiles_folders:
            for prj in self._profiles_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create profiles folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._profiles_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_profiles_folder, _ in self._profiles_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_profiles_folder,))

        for wl in self._queues_folders:
            for prj in self._queues_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create queues folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._queues_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_queues_folder, _ in self._queues_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_queues_folder,))

        for wl in self._positions_folders:
            for prj in self._positions_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create positions folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._positions_folders[wl][prj]]
                        )
                    )
                )

        for webadmin_positions_folder, _ in self._positions_folder_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_positions_folder,))

        for wl in self._positions:
            for prj in self._positions[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create positions: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._positions[wl][prj]]
                        )
                    )
                )

        for webadmin_positions, _ in self._position_updates:
            prompt.sendLine("- Synchronise %s" % (webadmin_positions,))

        for wl in self._calendars:
            for prj in self._calendars[wl]:
                if api_only:
                    prompt.sendLine(
                        "/!\\ 'api only' flag found - scenario object won't be migrated"
                    )
                prompt.sendLine(
                    "- [Project %s:%s] Create calendars: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._calendars[wl][prj]]
                        )
                    )
                )

        for wl in self._specialdays:
            for prj in self._specialdays[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create specialdays: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._specialdays[wl][prj]]
                        )
                    )
                )

        for wl in self._scenarios_folders:
            for prj in self._scenarios_folders[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create scenarios folders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._scenarios_folders[wl][prj]]
                        )
                    )
                )

        for wl in self._scenarios:
            for prj in self._scenarios[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create scenarios: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._scenarios[wl][prj]]
                        )
                    )
                )

        for wl in self._entrypoints:
            for prj in self._entrypoints[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create entrypoints: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._entrypoints[wl][prj]]
                        )
                    )
                )

        for wl in self._soundfiles_folders:
            for prj in self._soundfiles_folders[wl]:
                if api_only:
                    prompt.sendLine(
                        "/!\\ 'api only' flag found - scenario object won't be migrated"
                    )
                prompt.sendLine(
                    "- [Project %s:%s] Create soundfilesfolders: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._soundfiles_folders[wl][prj]]
                        )
                    )
                )

        for wl in self._soundfiles:
            for prj in self._soundfiles[wl]:
                prompt.sendLine(
                    "- [Project %s:%s] Create soundfiles: %s" % (
                        wl, prj, ', '.join(
                            [x.name for x in self._soundfiles[wl][prj]]
                        )
                    )
                )

        if not quiet:
            prompt.ask("Execute").addCallback(self.execute, has_calendars, has_soundfilesfolders, api_only)

        else:
            self.execute(True, has_calendars, has_soundfilesfolders, api_only)

    def _execute_create_whitelabels(self):
        if len(self._whitelabels) == 0:
            return defer.succeed(None)

        deferreds = []
        for wl in self._whitelabels:
            deferreds.append(wl.create())

        return defer.DeferredList(deferreds)

    @defer.inlineCallbacks
    def _execute_create_projects(self, _):
        if len(self._projects) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._projects:
            limit = len(self._projects[wl])
            offset = 0
            while offset <= limit:
                for prj in self._projects[wl][offset:offset + VERIFY_RANGE['projects']]:
                    deferreds.append(prj.create())

                offset += VERIFY_RANGE['projects']

                results += yield defer.gatherResults(deferreds)
                deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_profiles(self, _):
        if len(self._profiles) == 0:
            defer.returnValue(None)

        results = []

        for wl in self._profiles:
            for prj in self._profiles[wl]:
                for profile in self._profiles[wl][prj]:
                    result = yield profile.create()
                    results.append(result)

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_profiles(self, _):
        if len(self._profile_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._profile_updates)
        offset = 0

        while offset <= limit:
            for webadmin_profile, api_profile in self._profile_updates[offset:offset + VERIFY_RANGE['profiles']]:
                deferreds.append(webadmin_profile.update(api_profile))

            offset += VERIFY_RANGE['profiles']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_agents_folders(self, _):
        if len(self._agents_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._agents_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_agents_folder, api_agents_folder in \
                    self._agents_folder_updates[offset:offset + VERIFY_RANGE['agents_folders']]:
                deferreds.append(
                    webadmin_agents_folder.update(api_agents_folder)
                )

            offset += VERIFY_RANGE['agents_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_supervisors_folders(self, _):
        if len(self._supervisors_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._supervisors_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_users_folder, api_supervisors_folder in \
                    self._supervisors_folder_updates[offset:offset + VERIFY_RANGE['supervisors_folders']]:
                deferreds.append(
                    webadmin_users_folder.update(api_supervisors_folder)
                )

            offset += VERIFY_RANGE['supervisors_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_agents(self, _):
        if len(self._agents) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._agents:
            for prj in self._agents[wl]:
                limit = len(self._agents[wl][prj])
                offset = 0
                while offset <= limit:
                    for agent in self._agents[wl][prj][offset:offset + VERIFY_RANGE['agents']]:
                        deferreds.append(agent.create())

                    offset += VERIFY_RANGE['agents']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_agents(self, _):
        if len(self._agent_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._agent_updates)
        offset = 0

        while offset <= limit:
            for webadmin_agent, api_agent in self._agent_updates[offset:offset + VERIFY_RANGE['agents']]:
                deferreds.append(webadmin_agent.update(api_agent))

            offset += VERIFY_RANGE['agents']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_supervisors(self, _):
        if len(self._supervisors) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._supervisors:
            for prj in self._supervisors[wl]:
                limit = len(self._supervisors[wl][prj])
                offset = 0
                while offset <= limit:
                    for supervisor in self._supervisors[wl][prj][offset:offset + VERIFY_RANGE['supervisors']]:
                        deferreds.append(supervisor.create())

                    offset += VERIFY_RANGE['supervisors']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_supervisors(self, _):
        if len(self._supervisor_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._supervisor_updates)
        offset = 0

        while offset <= limit:
            for webadmin_agent, api_supervisor in self._supervisor_updates[offset:offset + VERIFY_RANGE['supervisors']]:
                deferreds.append(webadmin_agent.update(api_supervisor))

            offset += VERIFY_RANGE['supervisors']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_vocal_queues(self, _):
        if len(self._vocal_queues) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._vocal_queues:
            for prj in self._vocal_queues[wl]:
                limit = len(self._vocal_queues[wl][prj])
                offset = 0

                while offset <= limit:
                    for vocal_queue in self._vocal_queues[wl][prj][offset:offset + VERIFY_RANGE['vocal_queues']]:
                        deferreds.append(vocal_queue.create())

                    offset += VERIFY_RANGE['vocal_queues']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_vocal_queues(self, _):
        if not len(self._vocal_queue_updates):
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._vocal_queue_updates)
        offset = 0

        while offset <= limit:
            for webadmin_vocal_queue, api_vocal_queue in \
                    self._vocal_queue_updates[offset:offset + VERIFY_RANGE['vocal_queues']]:
                deferreds.append(webadmin_vocal_queue.update(api_vocal_queue))

            offset += VERIFY_RANGE['vocal_queues']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_mail_queues(self, _):
        if len(self._mail_queues) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._mail_queues:
            for prj in self._mail_queues[wl]:
                limit = len(self._mail_queues[wl][prj])
                offset = 0
                while offset <= limit:
                    for mail_queue in self._mail_queues[wl][prj][offset:offset + VERIFY_RANGE['mail_queues']]:
                        deferreds.append(mail_queue.create())

                    offset += VERIFY_RANGE['mail_queues']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_mail_queues(self, _):
        if not len(self._mail_queue_updates):
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._mail_queue_updates)
        offset = 0

        while offset <= limit:
            for webadmin_mail_queue, api_mail_queue in \
                    self._mail_queue_updates[offset:offset + VERIFY_RANGE['mail_queues']]:
                deferreds.append(webadmin_mail_queue.update(api_mail_queue))

            offset += VERIFY_RANGE['mail_queues']

        results += yield defer.gatherResults(deferreds)
        deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_profiles_folders(self, _):
        if len(self._profiles_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._profiles_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_profiles_folder, api_profiles_folder in \
                    self._profiles_folder_updates[offset:offset + VERIFY_RANGE['profiles_folders']]:
                deferreds.append(
                    webadmin_profiles_folder.update(api_profiles_folder)
                )

            offset += VERIFY_RANGE['profiles_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_transfer_targets_folders(self, _):
        if len(self._transfer_targets_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._transfer_targets_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_transfer_targets_folder, api_transfer_targets_folder in \
                    self._transfer_targets_folder_updates[offset:offset + VERIFY_RANGE['transfer_targets_folders']]:
                deferreds.append(
                    webadmin_transfer_targets_folder.update(api_transfer_targets_folder)
                )

            offset += VERIFY_RANGE['transfer_targets_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_transfer_targets(self, _):
        if len(self._transfer_targets) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._transfer_targets:
            for prj in self._transfer_targets[wl]:
                limit = len(self._transfer_targets[wl][prj])
                offset = 0
                while offset <= limit:
                    for transfer_target in self._transfer_targets[wl][prj][offset:offset + VERIFY_RANGE['transfer_targets']]:
                        deferreds.append(transfer_target.create())

                    offset += VERIFY_RANGE['transfer_targets']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_transfer_targets(self, _):
        if len(self._transfer_target_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._transfer_target_updates)
        offset = 0

        while offset <= limit:
            for webadmin_transfer_target, api_transfer_target in \
                    self._transfer_target_updates[offset:offset + VERIFY_RANGE['transfer_targets']]:
                deferreds.append(
                    webadmin_transfer_target.update(api_transfer_target)
                )

            offset += VERIFY_RANGE['transfer_targets']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_positions_folders(self, _):
        if len(self._positions_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._positions_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_positions_folder, api_positions_folder in \
                    self._positions_folder_updates[offset:offset + VERIFY_RANGE['positions_folders']]:
                deferreds.append(
                    webadmin_positions_folder.update(api_positions_folder)
                )

            offset += VERIFY_RANGE['positions_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_positions(self, _):
        if len(self._positions) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._positions:
            for prj in self._positions[wl]:
                limit = len(self._positions[wl][prj])
                offset = 0
                while offset <= limit:
                    for position in self._positions[wl][prj][offset:offset + VERIFY_RANGE['positions']]:
                        deferreds.append(position.create())

                    offset += VERIFY_RANGE['positions']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_positions(self, _):
        if len(self._position_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._position_updates)
        offset = 0

        while offset <= limit:
            for webadmin_position, api_position in \
                    self._position_updates[offset:offset + VERIFY_RANGE['positions']]:
                deferreds.append(
                    webadmin_position.update(api_position)
                )

            offset += VERIFY_RANGE['positions']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_update_scenarios_folders(self, _):
        if len(self._scenarios_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._scenarios_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_scenarios_folder, api_scenarios_folder in \
                    self._scenarios_folder_updates[offset:offset + VERIFY_RANGE['scenarios_folders']]:
                deferreds.append(
                    webadmin_scenarios_folder.update(api_scenarios_folder)
                )

            offset += VERIFY_RANGE['scenarios_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_scenarios(self, _):
        if len(self._scenarios) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._scenarios:
            for prj in self._scenarios[wl]:
                limit = len(self._scenarios[wl][prj])
                offset = 0
                while offset <= limit:
                    for scenario in self._scenarios[wl][prj][offset:offset + VERIFY_RANGE['scenarios']]:
                        deferreds.append(scenario.create())

                    offset += VERIFY_RANGE['scenarios']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_entrypoints(self, _):
        if len(self._entrypoints) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._entrypoints:
            for prj in self._entrypoints[wl]:
                limit = len(self._entrypoints[wl][prj])
                offset = 0
                while offset <= limit:
                    for entrypoint in self._entrypoints[wl][prj][offset:offset + VERIFY_RANGE['entrypoints']]:
                        deferreds.append(entrypoint.create())

                    offset += VERIFY_RANGE['entrypoints']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    def _execute_create_queues_folders(self, _):
        if len(self._queues_folders) == 0:
            return

        return self._create_generic_folders(self._queues_folders)

    def _execute_create_positions_folders(self, _):
        if len(self._positions_folders) == 0:
            return

        return self._create_generic_folders(self._positions_folders)

    def _execute_create_agents_folders(self, _):
        if len(self._agents_folders) == 0:
            return

        return self._create_generic_folders(self._agents_folders)

    def _execute_create_supervisors_folders(self, _):
        if len(self._supervisors_folders) == 0:
            return

        return self._create_generic_folders(self._supervisors_folders)

    def _execute_create_profiles_folders(self, _):
        if len(self._profiles_folders) == 0:
            return

        return self._create_generic_folders(self._profiles_folders)

    def _execute_create_transfer_targets_folders(self, _):
        if len(self._transfer_targets_folders) == 0:
            return

        return self._create_generic_folders(self._transfer_targets_folders)

    def _execute_create_scenarios_folders(self, _):
        if len(self._scenarios_folders) == 0:
            return

        return self._create_generic_folders(self._scenarios_folders)

    @defer.inlineCallbacks
    def _create_generic_folders(self, folders):
        deferreds = []
        results = []

        for wl in folders:
            for prj in folders[wl]:
                tree = self.build_folder_list_tree(folders[wl][prj])
                for _id in tree:
                    for folder in tree[_id]:
                        deferreds.append(folder.create())

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    def build_folder_list_tree(self, folders):
        tree = OrderedDict([(0, [])])
        folders_stack = list(folders)
        while folders_stack:
            check = len(folders_stack)

            for folder in list(folders_stack):
                if folder.config('parent_id') in tree:
                    tree[folder.config('parent_id')].append(folder)
                    tree[folder.config('id')] = []
                    folders_stack.remove(folder)

            if len(folders_stack) == check:
                log.msg("ERROR: orphan folders ? : %s " % folders_stack)
                break

        return tree

    @defer.inlineCallbacks
    def _execute_update_queues_folders(self, _):
        if len(self._queues_folder_updates) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        limit = len(self._queues_folder_updates)
        offset = 0

        while offset <= limit:
            for webadmin_queues_folder, api_queues_folder in \
                    self._queues_folder_updates[offset:offset + VERIFY_RANGE['queues_folders']]:
                deferreds.append(
                    webadmin_queues_folder.update(api_queues_folder)
                )

            offset += VERIFY_RANGE['queues_folders']

            results += yield defer.gatherResults(deferreds)
            deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_calendars(self, _, api_only):
        if len(self._calendars) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._calendars:
            for prj in self._calendars[wl]:
                limit = len(self._calendars[wl][prj])
                offset = 0
                while offset <= limit:
                    for calendar in self._calendars[wl][prj][offset:offset + VERIFY_RANGE['calendars']]:
                        deferreds.append(calendar.create(api_only))

                    offset += VERIFY_RANGE['calendars']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_specialdays(self, _):
        if len(self._specialdays) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._specialdays:
            for prj in self._specialdays[wl]:
                limit = len(self._specialdays[wl][prj])
                offset = 0
                while offset <= limit:
                    for specialday in self._specialdays[wl][prj][offset:offset + VERIFY_RANGE['specialdays']]:
                        deferreds.append(specialday.create())

                    offset += VERIFY_RANGE['specialdays']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def generate_calendars_tree(self, _):
        projects = []

        for wl in self._calendars:
            for prj in self._calendars[wl]:
                projects.append({
                    'whitelabel': wl,
                    'project': prj,
                    'customer_id': self._calendars[wl][prj][0].customer_id
                })

        projects_data = self.get_project_values(projects)
        yield self.process_calendar_tree(projects_data)

    @defer.inlineCallbacks
    def generate_soundfilesfolders_tree(self, _):
        projects = []

        for wl in self._soundfiles_folders:
            for prj in self._soundfiles_folders[wl]:
                projects.append({
                    'whitelabel': wl,
                    'project': prj,
                    'customer_id': self._soundfiles_folders[wl][prj][0].customer_id
                })

        projects_data = self.get_soundfile_project_values(projects)
        yield self.process_soundfile_folder_tree(projects_data)

    def get_project_values(self, values):
        projects = []
        for project in values:
            d = self._db_client.query_db(
                "select cal.nom, cal.id, cal.ppid, cal2.nom as parent_name, cal.user "
                "from adm_special_days as cal "
                "left outer join adm_special_days as cal2 on cal2.id=cal.ppid "
                "where cal.type = 'folder' "
                "and cal.user in (%s) "
                "order by cal.ppid" % (project['customer_id'],)
            )
            d.addCallback(self._build_tree, project)
            d.addCallback(self._get_api_calendars)
            projects.append(d)
        return projects

    def get_soundfile_project_values(self, values):
        projects = []
        for project in values:
            d = self._db_client.query_db(
                "select fol.displayname, fol.id, fol.ppid, "
                "fol2.displayname "
                "from adm_wwwuploaded as fol "
                "left outer join adm_wwwuploaded as fol2 on fol2.id=fol.ppid "
                "where fol.type='folder' and fol.user in (%s) "
                "order by fol.ppid" % (project['customer_id'],)
            )
            d.addCallback(self._build_tree, project)
            d.addCallback(self._get_api_soundfiles_folders)
            projects.append(d)
        return projects

    def _build_tree(self, result, project):
        tree = {0: []}
        identity = {'root': 0}
        reverse_identity = {0: 'root'}
        for row in result:
            identity[row[0]] = row[1]
            reverse_identity[int(row[1])] = row[0]
            tree.setdefault(int(row[2]), [])
            tree.setdefault(int(row[1]), [])
            tree[int(row[2])].append(int(row[1]))
            tree[int(row[2])] = sorted(tree[int(row[2])])
        project['tree'] = tree
        project['identity'] = identity
        project['reverse_identity'] = reverse_identity
        project['result'] = result
        return project

    @defer.inlineCallbacks
    def _get_api_calendars(self, project):
        try:
            data = yield self._client._client.calendars.read_all(
                whitelabel=project['whitelabel'], project=project['project']
            )
        except TrestNoContent:
            project['api'] = []

        else:
            project['api'] = data

        defer.returnValue(project)

    @defer.inlineCallbacks
    def _get_api_soundfiles_folders(self, project):
        try:
            data = yield self._client._client.soundfilesfolders.read_all(
                whitelabel=project['whitelabel'], project=project['project']
            )
        except TrestNoContent:
            project['api'] = []

        else:
            project['api'] = data

        defer.returnValue(project)

    @defer.inlineCallbacks
    def process_calendar_tree(self, res):
        results = yield defer.gatherResults(res)
        for result in results:
            if not result['tree'][0]:
                log.msg('[%s/%s][Webadmin] No calendars found' % (result['whitelabel'], result['project']))

            elif not result['api']:
                log.msg('[%s/%s][API] No calendars found' % (result['whitelabel'], result['project']))

            else:
                log.msg('[%s/%s] Processing calendars ...' % (result['whitelabel'], result['project']))

                for calendar in result['api']:
                    wa_id = result['identity'][calendar['name']]
                    for ppid in result['tree']:
                        if wa_id in result['tree'][ppid]:
                            wa_ppid = ppid
                            break

                    parent_name = result['reverse_identity'][wa_ppid]
                    if parent_name == 'root':
                        parent_id = 0

                    else:
                        for _calendar in result['api']:
                            if parent_name == _calendar['name']:
                                parent_id = _calendar['id']
                                break

                    try:
                        yield self._client._client.calendars.update_one(
                            str(calendar['id']), parent_id=str(parent_id),
                            whitelabel=calendar['whitelabel'], project=calendar['project']
                        )

                    except Exception as e:
                        log.msg(
                            "[%s/%s]"
                            "[calendar_name: %s, calendar_id: %s, parent_name:%s, parent_id: %s] "
                            "We got an error: %s" % (
                                calendar['whitelabel'], calendar['project'],
                                calendar['name'], calendar['id'],
                                parent_name, parent_id, str(e)
                            )
                        )

                    log.msg(
                        "[%s/%s] Calendar: %s added to : %s (%s->%s)" % (
                            calendar['whitelabel'], calendar['project'],
                            calendar['name'], parent_name, calendar['id'], parent_id
                        )
                    )

    @defer.inlineCallbacks
    def process_soundfile_folder_tree(self, res):
        results = yield defer.gatherResults(res)
        for result in results:
            if not result['tree'][0]:
                log.msg('[%s/%s][Webadmin] No soundfile folders found' % (result['whitelabel'], result['project']))

            elif not result['api']:
                log.msg('[%s/%s][API] No soundfile folders' % (result['whitelabel'], result['project']))

            else:
                log.msg('[%s/%s] Processing scenario folders ...' % (result['whitelabel'], result['project']))

                for folder in result['api']:
                    wa_id = result['identity'][folder['name']]
                    for ppid in result['tree']:
                        if wa_id in result['tree'][ppid]:
                            wa_ppid = ppid
                            break

                    parent_name = result['reverse_identity'][wa_ppid]
                    if parent_name == 'root':
                        parent_id = 0

                    else:
                        for _folder in result['api']:
                            if parent_name == _folder['name']:
                                parent_id = _folder['id']
                                break

                    try:
                        if folder['id'] != 0:
                            yield self._client._client.soundfilesfolders.update_one(
                                str(folder['id']), parent_id=str(parent_id), name=folder['name'],
                                whitelabel=folder['whitelabel'], project=folder['project']
                            )

                        else:
                            log.msg('Skipping root folder.')

                    except Exception as e:
                        log.msg(
                            "[%s/%s]"
                            "[folder_name: %s, folder_id: %s, parent_name:%s, parent_id: %s] "
                            "We got an error: %s" % (
                                folder['whitelabel'], folder['project'],
                                folder['name'], folder['id'],
                                parent_name, parent_id, str(e)
                            )
                        )
                    if folder['id'] != 0:
                        log.msg(
                            "[%s/%s] Soundfile folder: %s added to : %s (%s->%s)" % (
                                folder['whitelabel'], folder['project'],
                                folder['name'], parent_name, folder['id'], folder
                            )
                        )

    @defer.inlineCallbacks
    def _execute_create_soundfilesfolders(self, _):
        if len(self._soundfiles_folders) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._soundfiles_folders:
            for prj in self._soundfiles_folders[wl]:
                limit = len(self._soundfiles_folders[wl][prj])
                offset = 0
                while offset <= limit:
                    for folder in self._soundfiles_folders[wl][prj][offset:offset + VERIFY_RANGE['soundfilesfolders']]:
                        deferreds.append(folder.create())

                    offset += VERIFY_RANGE['soundfilesfolders']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    @defer.inlineCallbacks
    def _execute_create_soundfiles(self, _, api_only):
        if len(self._soundfiles) == 0:
            defer.returnValue(None)

        deferreds = []
        results = []

        for wl in self._soundfiles:
            for prj in self._soundfiles[wl]:
                limit = len(self._soundfiles[wl][prj])
                offset = 0
                while offset <= limit:
                    for soundfile in self._soundfiles[wl][prj][offset:offset + VERIFY_RANGE['soundfiles']]:
                        deferreds.append(soundfile.create(api_only))

                    offset += VERIFY_RANGE['soundfiles']

                    results += yield defer.gatherResults(deferreds)
                    deferreds = []

        defer.returnValue(results)

    def execute_end(self, _=None):
        if WARNS:
            for warn in WARNS:
                log.msg(warn)

        if ERRORS:
            for tag in ERRORS:
                for ressource, action in ERRORS[tag]:
                    log.msg(
                        "ERROR %s [%s] got %s errors (%s)" % (
                            tag, ressource, ERRORS[tag][(ressource, action)],
                            action
                        )
                    )

        reactor.stop()  # pylint: disable=E1101

    def execute(self, do_it_now, has_calendars, has_soundfilesfolders, api_only):
        if not do_it_now:
            log.msg("Transaction cancelled by user.")
            self.execute_end()

        else:
            log.msg("Here we go!")

            d = self._execute_create_whitelabels()
            d.addCallback(self._execute_create_projects)
            d.addCallback(self._execute_create_queues_folders)
            d.addCallback(self._execute_update_queues_folders)
            d.addCallback(self._execute_create_vocal_queues)
            d.addCallback(self._execute_update_vocal_queues)
            d.addCallback(self._execute_create_mail_queues)
            d.addCallback(self._execute_update_mail_queues)
            d.addCallback(self._execute_create_profiles_folders)
            d.addCallback(self._execute_update_profiles_folders)
            d.addCallback(self._execute_create_profiles)
            d.addCallback(self._execute_update_profiles)
            d.addCallback(self._execute_create_positions_folders)
            d.addCallback(self._execute_update_positions_folders)
            d.addCallback(self._execute_create_positions)
            d.addCallback(self._execute_update_positions)
            d.addCallback(self._execute_create_agents_folders)
            d.addCallback(self._execute_update_agents_folders)
            d.addCallback(self._execute_create_supervisors_folders)
            d.addCallback(self._execute_update_supervisors_folders)
            d.addCallback(self._execute_create_agents)
            d.addCallback(self._execute_update_agents)
            d.addCallback(self._execute_create_supervisors)
            d.addCallback(self._execute_update_supervisors)
            d.addCallback(self._execute_create_transfer_targets_folders)
            d.addCallback(self._execute_update_transfer_targets_folders)
            d.addCallback(self._execute_create_transfer_targets)
            d.addCallback(self._execute_update_transfer_targets)
            d.addCallback(self._execute_create_calendars, api_only)
            d.addCallback(self._execute_create_specialdays)
            d.addCallback(self._execute_create_scenarios_folders)
            d.addCallback(self._execute_update_scenarios_folders)
            d.addCallback(self._execute_create_scenarios)
            d.addCallback(self._execute_create_entrypoints)
            d.addCallback(self._execute_create_soundfilesfolders)
            d.addCallback(self._execute_create_soundfiles, api_only)
            if has_calendars:
                d.addCallback(self.generate_calendars_tree)

            if has_soundfilesfolders:
                d.addCallback(self.generate_soundfilesfolders_tree)

            d.addCallback(self.execute_end)  # pylint: disable=E1101


class Prompt(object, basic.LineReceiver):
    from os import linesep as delimiter  # NOQA

    def __init__(self, question):
        super(Prompt, self).__init__()
        self._ignore_input = True
        self._question = question

    def connectionMade(self):  # NOQA
        self.sendLine("")
        self.sendLine(self._question)
        self.sendLine("")

    def ask(self, prompt):
        self.sendLine("")
        self.sendLine("%s? [yes]" % (prompt,))

        self._ignore_input = False
        self.deferred = defer.Deferred()
        return self.deferred

    def lineReceived(self, line):  # NOQA
        if self._ignore_input:
            return

        else:
            self._ignore_input = True
            self.sendLine("")

            line = line.strip()
            if len(line) == 0 or line.lower() == 'y' or line.lower() == 'yes':
                self.deferred.callback(True)

            else:
                self.deferred.callback(False)
