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

import sys
import httplib
import urllib2

try:
    import phpserialize
except ImportError:
    print("Please install `phpserialize`.")
    print()
    print("\tpip install phpserialize")
    sys.exit(-1)

from collections import deque
from operator import itemgetter
from ivsync.utils import BusinessObject, handle_error, format_language
from twisted.python import log
from twisted.internet import defer

WARNS = []


class WebAdminWhitelabel(BusinessObject):
    def __str__(self):
        return "Whitelabel `%s'" % self.name

    def get_projects(self, filter_project=None):
        query = ("select distinct(cccid) as projects "
                 "from adm_customers "
                 "where provider_id = %s")
        args = (self.name,)

        if filter_project:
            query += " and cccid = %s"
            args = (self.name, filter_project)

        d = self._client.query_portal(query, args)

        def build_objects(result):
            return [WebAdminProject(value[0], self._client, self)
                    for value in result]

        @defer.inlineCallbacks
        def get_customer_ids(projects):
            calls = [project.get_customer_id() for project in projects]
            yield defer.gatherResults(calls)
            defer.returnValue(projects)

        d.addCallbacks(build_objects, handle_error)
        d.addCallbacks(get_customer_ids, handle_error)
        return d


class WebAdminProject(BusinessObject):
    def __init__(self, name, client, whitelabel):
        super(WebAdminProject, self).__init__(name, client)
        self._whitelabel = whitelabel

        self._transfer_targets_folder_parent_ids = []
        self._profiles_folder_parent_ids = []
        self._agents_folder_parent_ids = []
        self._supervisors_folder_parent_ids = []
        self._queues_folder_parents_ids = []
        self._positions_folder_parent_ids = []
        self._calendars_parent_ids = []
        self._scenarios_folder_parent_ids = []
        self._soundfiles_folder_parent_ids = []

        self._orphan_transfer_target_folders_ids = []
        self._orphan_profile_folders_ids = []
        self._orphan_agent_folders_ids = []
        self._orphan_supervisor_folders_ids = []
        self._orphan_queue_folders_ids = []
        self._orphan_position_folders_ids = []
        self._orphan_calendars_ids = []
        self._orphan_scenario_folders_ids = []
        self._orphan_soundfile_folders_ids = []

        self._orphan_transfer_targets_ids = []
        self._orphan_profiles_ids = []
        self._orphan_agents_ids = []
        self._orphan_supervisors_ids = []
        self._orphan_mqueues_ids = []
        self._orphan_vqueues_ids = []
        self._orphan_positions_ids = []
        self._orphan_specialdays_ids = []
        self._orphan_scenarios_ids = []
        self._orphan_soundfiles_ids = []

        self._root_transfer_targets_ids = []
        self._root_positions_ids = []
        self._root_specialdays_ids = []
        self._root_soundfiles_ids = []

        self._default_wa_queues_values = [
            ('sound_file', 'announcement_waiting_sound', str, '0'),
            ('sound_file_holding', 'announcement_holding_sound', str, '0'),
            ('onRealWaitingTime', 'max_waiting_time', int, 0),
            ('onEstimatedWaitingTime', 'max_estimated_waiting_time', int, 0),
            ('overflow_queue', 'overflow_queue', int, 0),
            ('overflow_mode', 'overflow_estimated_waiting_time', int, 0),
            ('overflow_priority', 'overflow_priority', float, 0.0)
        ]

        self._default_wa_profiles_values = [
            ('vocalqueues', []),
            ('mailqueues', []),
            ('allow_free_position', False),
            ('allow_wrapup_bypass', False),
            ('agent_can_record', False),
            ('record_cancel_right', False),
            ('lock_indicators', False),
            ('lock_view_mode', False),
            ('lock_urls', False),
            ('extended_view', False),
            ('default_channel', 'iv-vocal-server'),
            ('default_state', 'inbound'),
            ('callerid_type', 'default'),
            ('callerid_freenumber', ''),
            ('outgoing_callerid_type', 'default'),
            ('outgoing_callerid_freenumber', ''),
            ('outgoing_agent_callerid_type', 'default'),
            ('outgoing_agent_callerid_freenumber', ''),
            ('open_URL', ''),
            ('open_H', 0),
            ('open_W', 0),
            ('open_TYPE', 'popup'),
            ('close_URL', ''),
            ('close_H', 0),
            ('close_W', 0),
            ('close_TYPE', 'popup'),
            ('outgoing_start_URL', ''),
            ('outgoing_start_H', 0),
            ('outgoing_start_W', 0),
            ('outgoing_start_TYPE', 'popup'),
            ('outgoing_end_URL', ''),
            ('outgoing_end_H', 0),
            ('outgoing_end_W', 0),
            ('outgoing_end_TYPE', 'popup'),
            ('mail_autowithdrawn_on_lost', 3),
            ('forcepause_count', 5),
            ('target', ''),
        ]
        self.customer_id = None

    def __str__(self):
        return "Project `%s:%s'" % (self._whitelabel.name, self.name)

    def get_customer_id(self):
        d = self._client.query_portal(
            "select distinct(customerid) from adm_customers "
            "where provider_id = %s and cccid = %s",
            (self._whitelabel.name, self.name))

        def cleanup_results(result):
            result = [value[0] for value in result]
            self.customer_id = ', '.join(str(x) for x in result)

        d.addCallbacks(cleanup_results, handle_error)

        return d

    def get_profiles_folders(self, sync):
        log.msg("Getting profiles folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_vocal_agents_profiles "
            "where type='folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,))

        def build_objects(result, sync):
            profiles_folders = [[]]
            ppid = 0
            i = 0
            self._profiles_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._profiles_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        profiles_folders.append([])
                    profiles_folders[i].append(
                        WebAdminProfilesFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_profile_folders_ids.append(row[1])

            sync.callback(True)
            return profiles_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_agents_folders(self, sync):
        log.msg("Getting agents folders for %s." % (self,))
        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_vocal_agents_users "
            "where type='folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,))

        def build_objects(result, sync):
            agents_folders = [[]]
            ppid = 0
            i = 0
            self._agents_folder_parent_ids = self.get_children(

                0, self.make_tree(result))
            for row in result:
                if row[2] in self._agents_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        agents_folders.append([])
                    agents_folders[i].append(
                        WebAdminAgentsFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_agent_folders_ids.append(row[1])

            sync.callback(True)
            return agents_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_agents(self, sync):
        def process(_):
            log.msg("Getting agents for %s." % (self,))

            d = self._client.query_db(
                "select users.nom, users.configuration, "
                "profiles.nom as profile_name, users.ppid , users.id "
                "from adm_vocal_agents_users as users, "
                "adm_vocal_agents_profiles as profiles "
                "where users.type = 'agent' and users.user in (%s) "
                "and substring_index(substring_index(substring_index("
                "users.configuration, '\"profile\";s:', -1), "
                "'\"', 2), '\"', -1) = profiles.id "
                "group by users.nom order by users.nom;" % (self.customer_id,))

            def build_objects(result):
                agents = [[]]
                for row in result:
                    if row[3] not in self._agents_folder_parent_ids:
                        self._orphan_agents_ids.append(row[4])

                    else:
                        name = row[0]
                        profile_name = row[2]
                        folder_ref = row[3]
                        try:
                            config = phpserialize.loads(row[1])

                        except:
                            log.msg("CRITICAL(Agents) Skip for bad serialisation: %s" % row)
                            continue
                        if config is not None:
                            if not config.get('onRealWaitingTime'):
                                config['onRealWaitingTime'] = 300

                            if not config.get('onEstimatedWaitingTime'):
                                config['onEstimatedWaitingTime'] = 720

                            if not config.get('sound_file'):
                                config['sound_file'] = ''

                            if not config.get('sound_file_holding'):
                                config['sound_file_holding'] = ''

                            if not config.get('connexion_mode'):
                                config['connexion_mode'] = 'web'

                            if not config.get('phone_login'):
                                config['phone_login'] = ''

                            if not config.get('phone_password'):
                                config['phone_password'] = ''

                            if not config.get('phonenumber'):
                                config['phonenumber'] = ''

                            agents[0].append(
                                WebAdminAgent(name, self._client, self, config,
                                            profile_name, folder_ref))

                        else:
                            log.msg(
                                "[%s/%s] Ignored agent [%s] empty configuration" % (
                                    self._whitelabel.name, self.name, row[0]
                                )
                            )

                if self._orphan_agent_folders_ids or self._orphan_agents_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan agent folder(s), "
                        "%s orphan agents." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_agent_folders_ids),
                            len(self._orphan_agents_ids)
                        )
                    )

                return agents

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallbacks(process)
        return sync

    def get_supervisors_folders(self, sync):
        log.msg("Getting supervisors folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_vocal_supervisors "
            "where type='folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,))

        def build_objects(result, sync):
            supervisors_folders = [[]]
            ppid = 0
            i = 0
            self._supervisors_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._supervisors_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        supervisors_folders.append([])
                    supervisors_folders[i].append(
                        WebAdminSupervisorsFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )

                else:
                    self._orphan_supervisor_folders_ids.append(row[1])

            sync.callback(True)
            return supervisors_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_supervisors(self, sync):
        def process(_):
            log.msg("Getting supervisor for %s." % (self,))

            d = self._client.query_db(
                "SELECT S.nom, S.configuration, A.configuration, S.ppid, AP.nom "
                "FROM adm_vocal_supervisors AS S "
                "LEFT OUTER JOIN adm_vocal_agents_users AS A "
                "ON CONCAT('AGENT', S.nom) = A.nom AND A.type = '' and A.user = S.user "
                "LEFT OUTER JOIN adm_vocal_agents_profiles AS AP "
                "ON substring_index(substring_index(substring_index("
                "A.configuration, '\"profile\";s:', -1), "
                "'\"', 2), '\"', -1) = AP.id "
                "WHERE S.user = %s "
                "AND S.type='supervisor' "
                "GROUP BY S.nom "
                "ORDER BY S.nom" % (self.customer_id,))

            d.addCallbacks(self._get_configs_sup, handle_error)
            d.addCallbacks(self._ask_supervised_data, handle_error)
            d.addCallbacks(self._build_configs_sup, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def _get_configs_sup(self, result):
        configs = []
        for row in result:
            if row[3] not in self._supervisors_folder_parent_ids:
                self._orphan_supervisors_ids.append(row[3])

            else:
                name = row[0]
                folder_ref = row[3]
                profile = row[4]

                if not row[1] or row[1] == 'N;':
                    continue

                sup_config = phpserialize.loads(row[1])

                if row[2] and row[2] != 'N;':
                    ag_config = phpserialize.loads(row[2])
                else:
                    ag_config = {}

                if ag_config is None:
                    ag_config = {}

                if not ag_config.get('onRealWaitingTime'):
                    ag_config['onRealWaitingTime'] = 300

                if not ag_config.get('onEstimatedWaitingTime'):
                    ag_config['onEstimatedWaitingTime'] = 720

                if not ag_config.get('sound_file'):
                    ag_config['sound_file'] = ''

                if not ag_config.get('sound_file_holding'):
                    ag_config['sound_file_holding'] = ''

                if not ag_config.get('connexion_mode'):
                    ag_config['connexion_mode'] = 'web'

                if not ag_config.get('phone_login'):
                    ag_config['phone_login'] = ''

                if not ag_config.get('phone_password'):
                    ag_config['phone_password'] = ''

                if not ag_config.get('phonenumber'):
                    ag_config['phonenumber'] = ''

                if not sup_config.get('spy_right'):
                    sup_config['spy_right'] = True

                if not sup_config.get('sup_can_record'):
                    sup_config['sup_can_record'] = False

                if not sup_config.get('sup_can_consult_record'):
                    sup_config['sup_can_consult_record'] = False

                if sup_config is not None:
                    configs.append((name, sup_config, ag_config, folder_ref, profile))

                else:
                    log.msg(
                        "[%s/%s] Ignored supervisor [%s] empty configuration" % (
                            self._whitelabel.name, self.name, row[0]
                        )
                    )

        return configs

    def _ask_supervised_data(self, configs):
        deferreds = []
        for config in configs:
            if config[1].get('selectedProfiles', []):
                ids = [_id for _id in config[1]['selectedProfiles'].split(',') if _id]

                if ids:
                    d = self._client.query_db((
                        "SELECT type, id, nom, ppid "
                        "FROM adm_vocal_agents_profiles "
                        "WHERE user = %s AND id IN (%s)" % (self.customer_id, ', '.join(ids))
                    ))
                    d.addCallbacks(self._process_data, handle_error, callbackArgs=[config])

                else:
                    config[1]['supervised_profiles'] = []
                    config[1]['supervised_profiles_folders'] = []
                    d = defer.succeed(config)

            else:
                config[1]['supervised_profiles'] = []
                config[1]['supervised_profiles_folders'] = []
                d = defer.succeed(config)

            deferreds.append(d)

        return defer.gatherResults(deferreds)

    def _process_data(self, results, config):
        config[1]['supervised_profiles'] = []
        config[1]['supervised_profiles_folders'] = []
        if results:
            for result in results:
                if result[0] == 'profile':
                    config[1]['supervised_profiles'].append(result[2])

                else:
                    config[1]['supervised_profiles_folders'].append(result[1])

        return config

    def _build_configs_sup(self, configs):
        supervisors = [[]]
        for config in configs:
            supervisors[0].append(
                WebAdminSupervisors(config[0], self._client, self, config[1], config[2], config[3], config[4])
            )

        if self._orphan_supervisor_folders_ids or self._orphan_supervisors_ids:
            WARNS.append(
                "WARN [%s/%s]: %s orphan supervisor folder(s), "
                "%s orphan supervisors." % (
                    self._whitelabel.name, self.name,
                    len(self._orphan_supervisor_folders_ids),
                    len(self._orphan_supervisors_ids)
                )
            )

        return supervisors

    def get_profiles(self, sync):
        def process(_):
            log.msg("Getting profiles for %s." % (self,))
            d = self._client.query_db(
                "select nom, configuration, ppid, dtemodified "
                "from adm_vocal_agents_profiles "
                "where type = 'profile' and user in (%s) "
                "and configuration is not NULL "
                "order by nom" % (self.customer_id,))

            d.addCallbacks(self._get_configs, handle_error)
            d.addCallbacks(self._ask_mail_queues, handle_error)
            d.addCallbacks(self._ask_vocal_queues, handle_error)
            d.addCallbacks(self._build_configs, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def _get_configs(self, result):
        configs = []
        for row in result:
            name = row[0]
            ppid = row[2]
            created_at = row[3]

            config = phpserialize.loads(row[1])
            if config is not None:
                config['created_at'] = str(created_at)
                configs.append((name, config, ppid))

            else:
                log.msg(
                    "[%s/%s] Ignored profile [%s] empty configuration" % (
                        self._whitelabel.name, self.name, row[0]
                    )
                )

        return configs

    def _ask_mail_queues(self, configs):
        deferreds = []
        for config in configs:
            if config[1].get('mqueuelinker', {}):
                mqueues = list(set(config[1]['mqueuelinker'].values()))
                if '' in mqueues:
                    mqueues.remove('')

                if mqueues:
                    d = self._client.query_db((
                        "select nom "
                        "from adm_vocal_queues "
                        "where type = 'mqueue' "
                        "and user in (%s) "
                        "and id in (%s)" % (self.customer_id, ', '.join(mqueues))
                    ))
                    d.addCallbacks(self._process_mqueues, handle_error,
                                callbackArgs=[config])

                else:
                    d = defer.succeed(config)
            else:
                d = defer.succeed(config)

            deferreds.append(d)

        return defer.gatherResults(deferreds)

    def _process_mqueues(self, result, config):
        if result:
            config[1]['mailqueues'] = list(result[0])

        else:
            config[1]['mailqueues'] = []

        return config

    def _ask_vocal_queues(self, configs):
        deferreds = []
        for config in configs:
            if config[1].get('queuelinker', {}):
                queues = [queue for queue in list(set(config[1]['queuelinker'].values())) if queue]

                if queues:
                    d = self._client.query_db((
                        "select configuration "
                        "from adm_vocal_queues "
                        "where type = 'queue' "
                        "and user in (%s) "
                        "and id in (%s) "
                        "and configuration is not NULL" % (self.customer_id, ', '.join(queues))
                    ))
                    d.addCallbacks(self._process_queues, handle_error,
                                callbackArgs=[config])

                else:
                    d = defer.succeed(config)

            else:
                d = defer.succeed(config)

            deferreds.append(d)

        return defer.gatherResults(deferreds)

    def _process_queues(self, configurations, config):
        config[1]['vocalqueues'] = []
        if configurations:
            for configuration in configurations:
                try:
                    _config = phpserialize.loads(configuration[0])

                except:
                    log.msg("CRITICAL(Profiles>VocalQueues)> Skip for bad serialisation: %s" % configuration)
                    continue
                config[1]['vocalqueues'].append(
                    {'name': _config['nom'],
                     'priority': configurations.index(configuration)}
                )

        return config

    def _build_configs(self, configs):
        profiles = [[]]
        for config in configs:
            if config[2] not in self._profiles_folder_parent_ids:
                self._orphan_profile_folders_ids.append(config[2])

            else:
                config[1]['tabs'] = []
                if config[1].get('urls'):
                    urls = config[1]['urls'].values()
                    urls_title = config[1]['urls_title'].values()
                    i = 0
                    for url in urls:
                        config[1]['tabs'].append(
                            {
                                'name': urls_title[urls.index(url)],
                                'index': i,
                                'url': url
                            },
                        )
                        i += 1

                # Default values if there are missing in 'configuration'
                for values in self._default_wa_profiles_values:
                    if not config[1].get(values[0]):
                        config[1][values[0]] = values[1]

                profiles[0].append(
                    WebAdminProfile(config[0], self._client, self, config[1], config[2])
                )

        if self._orphan_profile_folders_ids or self._orphan_profiles_ids:
            WARNS.append(
                "WARN [%s/%s]: %s orphan folder(s), %s orphan profile(s)." % (
                    self._whitelabel.name, self.name,
                    len(self._orphan_profile_folders_ids),
                    len(self._orphan_profiles_ids)
                )
            )

        return profiles

    def get_queues_folders(self, sync_vq, sync_mq):
        log.msg("Getting queues folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_vocal_queues "
            "where type='folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,))

        def build_objects(result, sync_vq, sync_mq):
            queues_folders = [[]]
            ppid = 0
            i = 0
            self._queues_folder_parents_ids = self.get_children(0, self.make_tree(result))
            for row in result:
                if row[2] in self._queues_folder_parents_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        queues_folders.append([])
                    queues_folders[i].append(
                        WebAdminQueuesFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_queue_folders_ids.append(row[1])

            sync_vq.callback(True)
            sync_mq.callback(True)
            return queues_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync_vq, sync_mq])
        return d

    def get_vocal_queues(self, sync):
        def process(_):
            log.msg("Getting vocal queues for %s." % (self,))

            d = self._client.query_db(
                "select nom, configuration, ppid, id "
                "from adm_vocal_queues "
                "where type = 'queue' and user in (%s) "
                "and configuration is not NULL "
                "order by nom" % (self.customer_id,)
            )

            def build_objects(result):
                vocal_queues = [[]]
                for row in result:
                    if row[1] in ('N;', ""):
                        log.msg(
                            "[%s/%s] Ignored queue [%s] empty configuration" % (
                                self._whitelabel.name, self.name, row[0]
                            )
                        )
                    else:
                        config = phpserialize.loads(row[1])
                        if row[2] not in self._queues_folder_parents_ids:
                            self._orphan_vqueues_ids.append(row[3])

                        elif config is not None:
                            name = config.get('nom', row[0]) if config else row[0]
                            _config = {'display_name': row[0], 'folder_ref': row[2]}
                            for w_key, a_key, _type, default in self._default_wa_queues_values:
                                _config[a_key] = _type(config[w_key]) if config.get(w_key) else default

                            vocal_queues[0].append(
                                WebAdminVocalQueue(
                                    name,
                                    self._client,
                                    self,
                                    _config
                                )
                            )

                        else:
                            log.msg(
                                "[%s/%s] Ignored queue [%s] empty configuration" % (
                                    self._whitelabel.name, self.name, row[0]
                                )
                            )

                if self._orphan_queue_folders_ids or self._orphan_vqueues_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan folder(s), "
                        "%s orphan vocalqueues(s)." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_queue_folders_ids),
                            len(self._orphan_vqueues_ids)
                        )
                    )

                return vocal_queues

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_mail_queues(self, sync):
        def process(_):
            log.msg("Getting mail queues for %s." % (self,))

            d = self._client.query_db(
                "select nom, configuration, ppid, id "
                "from adm_vocal_queues "
                "where type = 'mqueue' and user in (%s) "
                "order by nom" % (self.customer_id,)
            )

            def build_objects(result):
                mail_queues = [[]]
                for row in result:
                    if row[2] not in self._queues_folder_parents_ids:
                        self._orphan_mqueues_ids.append(row[3])

                    else:
                        name = row[0]
                        mail_queues[0].append(
                            WebAdminMailQueue(
                                name,
                                self._client,
                                self,
                                {
                                    'name': row[0],
                                    'folder_ref': row[2]
                                }
                            )
                        )

                if self._orphan_queue_folders_ids or self._orphan_mqueues_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan folder(s), "
                        "%s orphan mailqueue(s)." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_queue_folders_ids),
                            len(self._orphan_mqueues_ids)
                        )
                    )

                return mail_queues

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_children(self, token, tree):
        # http://kmkeen.com/python-trees/

        visited = set()
        to_crawl = deque([token])
        while to_crawl:
            current = to_crawl.popleft()
            if current in visited:
                continue
            visited.add(current)
            node_children = set(tree[current])
            to_crawl.extend(node_children - visited)
        return list(visited)

    def make_tree(self, result):
        tree = {0: []}
        for row in result:
            tree.setdefault(int(row[2]), [])
            tree.setdefault(int(row[1]), [])
            tree[int(row[2])].append(int(row[1]))
            tree[int(row[2])] = sorted(tree[int(row[2])])
        return tree

    def get_transfer_targets_folders(self, sync):
        log.msg("Getting transfer targets folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_numbers_pack "
            "where type = 'folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,)
        )

        def build_objects(result, sync):
            transfer_targets_folders = [[]]
            ppid = 0
            i = 0
            self._transfer_targets_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._transfer_targets_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        transfer_targets_folders.append([])
                    transfer_targets_folders[i].append(
                        WebAdminTransferTargetsFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_transfer_target_folders_ids.append(row[1])

            sync.callback(True)
            return transfer_targets_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_transfer_targets(self, sync):
        def process(_):
            log.msg("Getting transfer targets for %s." % (self,))

            d = self._client.query_db(
                "select prefix, number, ppid, description, extension, id "
                "from adm_numbers_pack "
                "where type = 'number' and user in (%s) " % (self.customer_id,)
            )

            def build_objects(result):
                transfer_targets = [[]]
                ppid = 0
                i = 0
                for row in result:
                    if int(row[2]) == 0:
                        self._root_transfer_targets_ids.append(row[5])

                    if row[2] not in self._transfer_targets_folder_parent_ids:
                        self._orphan_transfer_targets_ids.append(row[5])

                    else:
                        if ppid != row[2]:
                            ppid = row[2]
                            i += 1
                            transfer_targets.append([])
                        transfer_targets[i].append(
                            WebAdminTransferTargets(
                                row[1],
                                self._client,
                                self,
                                {
                                    'prefix': row[0],
                                    'folder_ref': row[2],
                                    'comment': row[3],
                                    'transferplus_number': row[4]
                                }
                            )
                        )

                if self._orphan_transfer_target_folders_ids or \
                        self._orphan_transfer_targets_ids or \
                        self._root_transfer_targets_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan folder(s), "
                        "%s orphan transfer target(s), "
                        "%s transfer target(s) in root directory." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_transfer_target_folders_ids),
                            len(self._orphan_transfer_targets_ids),
                            len(self._root_transfer_targets_ids)
                        )
                    )

                return transfer_targets

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_positions_folders(self, sync):
        log.msg("Getting positions folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_positions "
            "where type = 'folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,)
        )

        def build_objects(result, sync):
            positions_folders = [[]]
            ppid = 0
            i = 0
            self._positions_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._positions_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        positions_folders.append([])
                    positions_folders[i].append(
                        WebAdminPositionsFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_position_folders_ids.append(row[1])

            sync.callback(True)
            return positions_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_positions(self, sync):
        def process(_):
            log.msg("Getting positions for %s." % (self,))

            d = self._client.query_db(
                "select prefix, number, ppid, description, position, id "
                "from adm_positions "
                "where type = 'number' and user in (%s)" % (self.customer_id,)
            )

            def build_objects(result):
                positions = [[]]
                for row in result:
                    if row[2] not in self._positions_folder_parent_ids:
                        self._orphan_positions_ids.append(row[5])

                    else:
                        positions[0].append(
                            WebAdminPositions(
                                row[1],
                                self._client,
                                self,
                                {
                                    'prefix': row[0],
                                    'number': row[1],
                                    'folder_ref': row[2],
                                    'comment': row[3],
                                    'position': row[4]
                                }
                            )
                        )

                if self._orphan_position_folders_ids or \
                        self._orphan_positions_ids or \
                        self._root_positions_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan folder(s), "
                        "%s orphan position(s), "
                        "%s position(s) in root directory." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_position_folders_ids),
                            len(self._orphan_positions_ids),
                            len(self._root_positions_ids)
                        )
                    )
                return positions

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_scenarios_folders(self, sync):
        log.msg("Getting scenarios folders for %s." % (self,))

        d = self._client.query_db(
            "select nom, id, ppid "
            "from adm_vocal_scenarios  "
            "where type = 'folder' "
            "and user in (%s) "
            "order by ppid" % (self.customer_id,)
        )

        def build_objects(result, sync):
            scenarios_folders = [[]]
            ppid = 0
            i = 0
            self._scenarios_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._scenarios_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        scenarios_folders.append([])
                    scenarios_folders[i].append(
                        WebAdminScenariosFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'parent_id': row[2]}
                        )
                    )
                else:
                    self._orphan_scenario_folders_ids.append(row[1])

            sync.callback(True)
            return scenarios_folders

        d.addCallbacks(build_objects, handle_error, callbackArgs=[sync])
        return d

    def get_scenarios(self, sync):
        def process(_):
            log.msg("Getting scenarios for %s." % (self,))

            d = self._client.query_db(
                "select scenario.nom, scenario.ppid, scenario.id, folder.nom, scenario.dtemodified "
                "from adm_vocal_scenarios as scenario "
                "left outer join adm_vocal_scenarios as folder on scenario.ppid = folder.id "
                "where scenario.type = 'scenario' and scenario.user in (%s) and scenario.nom != ''" % (self.customer_id,)
            )

            def build_objects(result):
                scenarios = [[]]
                for row in result:
                    if row[1] not in self._scenarios_folder_parent_ids:
                        self._orphan_scenarios_ids.append(row[2])

                    else:
                        scenarios[0].append(
                            WebAdminScenarios(
                                row[0],
                                self._client,
                                self,
                                {
                                    'folder_ref': row[1],
                                    'folder_name': row[3],
                                    'updated_at': row[4]
                                }
                            )
                        )

                if self._orphan_scenario_folders_ids or \
                        self._orphan_scenarios_ids:
                    WARNS.append(
                        "WARN [%s/%s]: %s orphan folder(s), "
                        "%s orphan scenario(s)." % (
                            self._whitelabel.name, self.name,
                            len(self._orphan_scenario_folders_ids),
                            len(self._orphan_scenarios_ids),
                        )
                    )
                return scenarios

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_entrypoints(self, sync):
        def process(_):
            log.msg("Getting entrypoints for %s." % (self,))

            d = self._client.query_db(
                "select adm_activation.cccentrypoint, "
                "   adm_activation.numbertype, adm_activation.servicenumber, "
                "   adm_activation.commentaire, adm_activation.dtemodified, "
                "   adm_vocal_scenarios.nom, adm_activation.commentaire "
                "from adm_activation "
                "left outer join adm_vocal_scenarios "
                "   on adm_activation.projectid = adm_vocal_scenarios.id "
                "where adm_activation.numbertype in ('incall', 'webcall', 'callback') "
                "and adm_activation.cccentrypoint != '' "
                "and adm_activation.user in (%s)" % (self.customer_id,)
            )

            def build_objects(result):
                entrypoints = [[]]
                for row in result:
                    entrypoints[0].append(
                        WebAdminEntryPoints(
                            row[0],
                            self._client,
                            self,
                            {
                                'primary_data': row[0],
                                'auxiliary_data': row[2],
                                'type': 'vocal',
                                'sub_type': row[1],
                                'description': row[3],
                                'updated_at': row[4],
                                'scenario': row[5],
                                'commentary': row[6]
                            }
                        )
                    )

                return entrypoints

            d.addCallbacks(build_objects, handle_error)
            return d

        sync.addCallback(process)
        return sync

    def get_calendars(self):
        log.msg("Getting calendars for %s." % (self,))

        d = self._client.query_db(
            "select cal.nom, cal.id, cal.ppid, cal2.nom as parent_name, cal.user "
            "from adm_special_days as cal "
            "left outer join adm_special_days as cal2 on cal2.id=cal.ppid "
            "where cal.type = 'folder' "
            "and cal.user in (%s) "
            "order by cal.ppid" % (self.customer_id,)
        )

        def build_objects(result):
            calendars = [[]]
            ppid = 0
            i = 0
            self._calendars_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._calendars_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        calendars.append([])
                    calendars[i].append(
                        WebAdminCalendars(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'customer_id': row[4]},
                            {'parent_name': row[3] if row[3] else 0}
                        )
                    )
                else:
                    self._orphan_calendars_ids.append(row[1])

            return calendars

        d.addCallbacks(build_objects, handle_error)
        return d

    def get_specialdays(self):
        log.msg("Getting specialdays for %s." % (self,))

        d = self._client.query_db(
            "select sd.day, sd.day_stop, sd.ppid, cal.nom, sd.dtemodified "
            "from adm_special_days as sd "
            "join adm_special_days as cal on cal.id=sd.ppid "
            "where sd.type = 'day' "
            "and sd.user in (%s) "
            "and cal.nom is not null" % (self.customer_id,)
        )

        def build_objects(result):
            specialdays = [[]]
            for row in result:
                specialdays[0].append(
                    WebAdminSpecialDays(
                        self._client,
                        self,
                        {
                            'start_date': row[0],
                            'end_date': row[1],
                            'calendar_name': row[3],
                            'updated_at': row[4]
                        }
                    )
                )

            if self._orphan_specialdays_ids or \
                    self._root_specialdays_ids:
                WARNS.append(
                    "WARN [%s/%s]: %s orphan specialday(s), "
                    "%s specialday(s) in root directory." % (
                        self._whitelabel.name, self.name,
                        len(self._orphan_specialdays_ids),
                        len(self._root_specialdays_ids)
                    )
                )
            return specialdays

        d.addCallbacks(build_objects, handle_error)
        return d

    def get_soundfiles_folders(self):
        log.msg("Getting soundfiles folders for %s." % (self,))

        d = self._client.query_db(
            "select fol.displayname, fol.id, fol.ppid, "
            "fol2.displayname as parent_name, fol.user "
            "from adm_wwwuploaded as fol "
            "left outer join adm_wwwuploaded as fol2 on fol2.id=fol.ppid "
            "where fol.type='folder' and fol.user in (%s) "
            "order by fol.ppid" % (self.customer_id,)
        )

        def build_objects(result):
            folders = [[]]
            ppid = 0
            i = 0
            self._soundfiles_folder_parent_ids = self.get_children(
                0, self.make_tree(result))
            for row in result:
                if row[2] in self._soundfiles_folder_parent_ids:
                    if ppid != row[2]:
                        ppid = row[2]
                        i += 1
                        folders.append([])
                    folders[i].append(
                        WebAdminSoundFilesFolders(
                            row[0],
                            self._client,
                            self,
                            {'id': row[1], 'customer_id': row[4]},
                            {'parent_name': row[3] if row[3] else 0}
                        )
                    )
                else:
                    self._orphan_scenario_folders_ids.append(row[1])

            return folders

        d.addCallbacks(build_objects, handle_error)
        return d

    def get_soundfiles(self):
        log.msg("Getting soundfiles for %s." % (self,))

        d = self._client.query_db(
            "select file.displayname, file.diskname, "
            "   file.type, file.ppid, folder.displayname as file_folder, "
            "   file.user, file.id, tts_history.tts_text, tts_history.tts_voice, "
            "   file.dteinserted "
            "from adm_wwwuploaded as file "
            "left outer join adm_wwwuploaded as folder "
            "   on folder.id = file.ppid and folder.type = 'folder' "
            "left outer join tts_history "
            "   on tts_history.diskname COLLATE latin1_general_ci = file.diskname COLLATE latin1_general_ci "
            "   and file.type ='tts/wav' "
            "where file.type != 'folder' "
            "and file.diskname like '%%.wav%%' "
            "and file.user in (%s)" % (self.customer_id,)
        )

        def build_objects(result):
            files = [[]]
            unique_dict = {}
            _result = []
            for row in result:
                _row = list(row)
                if _row[0].upper() not in unique_dict:
                    unique_dict[_row[0].upper()] = 0
                else:
                    unique_dict[_row[0].upper()] += 1
                    _row[0] = _row[0] + "_%s" % (str(unique_dict[_row[0].upper()]),)

                _result.append(_row)
            result = _result

            for row in result:
                if row[2] == 'tts/wav':
                    metadata = {'tts_voice': row[8], 'tts_text': row[7]}
                else:
                    metadata = {}
                url = "http://%s/objects/custom/public/%s/%s" % (
                    self._client._wa_host, self.customer_id, row[1])

                req = urllib2.Request(url)
                try:
                    res = urllib2.urlopen(req)

                except urllib2.HTTPError as e:
                    WARNS.append(
                        "WARN [%s/%s]: Can't access file (displayname:%s/folder:%s) on %s. %s" % (
                            self._whitelabel.name, self.name, row[0], row[4], url, str(e)
                        )
                    )
                    continue

                if res.getcode() != 200:
                    WARNS.append(
                        "WARN [%s/%s]: Can't access file (displayname:%s/folder:%s) on %s. [code: %s]" % (
                            self._whitelabel.name, self.name, row[0], row[4], url, res.getcode()
                        )
                    )
                else:
                    files[0].append(
                        WebAdminSoundFiles(
                            self._client,
                            self,
                            {'id': row[6], 'customer_id': row[5]},
                            {
                                'display_name': row[0],
                                'url': url,
                                'type': 'tts/wav' if row[2] == 'tts/wav' else 'audio/wav',
                                'folder_name': row[4] if row[4] else 'root',
                                'metadata': metadata,
                                'created_at': str(row[9]),
                                'path': row[1]
                            }
                        )
                    )

            if self._orphan_soundfiles_ids or \
                    self._root_soundfiles_ids:
                WARNS.append(
                    "WARN [%s/%s]: %s orphan soundfile(s), "
                    "%s soundfile(s) in root directory." % (
                        self._whitelabel.name, self.name,
                        len(self._orphan_soundfiles_ids),
                        len(self._root_soundfiles_ids)
                    )
                )
            WARNS.append('(%s/%s)[%s/%s] SoundFiles migrated.' % (
                self._whitelabel.name, self.name,
                len(files[0]), len(result))
            )
            return files

        d.addCallbacks(build_objects, handle_error)
        return d


class WebAdminAgentsFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminAgentsFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'AgentsFolder `%s (%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_agents_folder, transaction):
        if not api_agents_folder.exists():
            return

        if self.name != api_agents_folder.name:
            transaction.update_agents_folder(
                self, api_agents_folder)

    def update(self, api_agents_folder):
        api_agents_folder.config('name', self.config('name'))
        if api_agents_folder.exists():
            return api_agents_folder.save()
        else:
            return api_agents_folder.create()


class WebAdminAgent(BusinessObject):
    configuration_keys = [
        'display_name', 'language', 'email', 'profile',
        'folder_ref'
    ]

    encrypted_configuration_keys = ['password', 'phone_password']

    valid_keys_defaults = {
        'nom': 'display_name',
        'lang': 'language',
        'email': 'email',
        'login': 'login',
        'ppid': 'folder_id',
        'password': 'password',
        'phone_login': 'phone_login',
        'phone_password': 'phone_password',
        'phonenumber': 'phone_number',
        'sound_file': 'announcement_waiting_sound',
        'sound_file_holding': 'announcement_holding_sound',
        'connexion_mode': 'connection_mode'
    }

    valid_keys_int = {
        'onRealWaitingTime': 'max_waiting_time',
        'onEstimatedWaitingTime': 'max_estimated_waiting_time',
    }

    def __init__(self, name, client, project, configuration, profile, folder_ref):
        super(WebAdminAgent, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._profile = profile
        self._data = {'email': ''}
        self.name = configuration['login']
        self._data['folder_ref'] = folder_ref

        self._filter_useful_configuration(configuration)

    def _filter_useful_configuration(self, configuration):
        for key in self.valid_keys_defaults:
            if key in configuration:
                if key == 'lang':

                    self._data[self.valid_keys_defaults[key]] = \
                        format_language(configuration[key])
                else:
                    self._data[self.valid_keys_defaults[key]] = configuration[key]

        for key in self.valid_keys_int:
            if key in configuration:
                self._data[self.valid_keys_int[key]] = int(configuration[key] or 0)

        self._data['project'] = self._project.name
        self._data['whitelabel'] = self._whitelabel.name

    def config(self, key):
        if key == 'profile':
            return self._profile
        else:
            return self._data.get(key)

    def __str__(self):
        return 'Agent `%s@%s:%s`' % (self.name, self._whitelabel.name,
                                     self._project.name)

    @defer.inlineCallbacks
    def compare(self, api_agent, transaction):
        if api_agent.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_agent.config(key):
                    transaction.update_ressource('agents', self, api_agent)
                    return
            try:
                yield api_agent.check_pwds(self.config('password'), self.config('phone_password'))

            except:
                transaction.update_ressource('agents', self, api_agent)
                return

    def update(self, api_agent):
        for key in self.configuration_keys:
            api_agent.config(key, self.config(key))

        for key in self.encrypted_configuration_keys:
            api_agent.config(key, self.config(key))

        if api_agent.exists():
            return api_agent.save()
        else:
            return api_agent.create()


class WebAdminSupervisorsFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminSupervisorsFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'SupervisorsFolder `%s (%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_supervisors_folder, transaction):
        if not api_supervisors_folder.exists():
            return

        if self.name != api_supervisors_folder.name:
            transaction.update_agents_folder(
                self, api_supervisors_folder)

    def update(self, api_supervisors_folder):
        api_supervisors_folder.config('name', self.config('name'))
        if api_supervisors_folder.exists():
            return api_supervisors_folder.save()
        else:
            return api_supervisors_folder.create()


class WebAdminSupervisors(BusinessObject):
    configuration_keys = [
        'display_name', 'language', 'email', 'profile',
        'folder_ref', 'phone_login', 'phone_number', 'max_waiting_time',
        'max_estimated_waiting_time', 'announcement_waiting_sound',
        'announcement_holding_sound', 'connection_mode', 'allow_spy_right',
        'make_record_right', 'consult_record_right',
    ]
    list_configuration_keys = ['supervised_profiles', 'supervised_profiles_folders']
    encrypted_configuration_keys = ['password', 'phone_password']

    valid_keys_defaults = {
        'nom': 'display_name',
        'lang': 'language',
        'email': 'email',
        'login': 'login',
        'ppid': 'folder_ref',
        'password': 'password',

        # AG SUP
        'phone_login': 'phone_login',
        'phone_password': 'phone_password',
        'phonenumber': 'phone_number',
        'sound_file': 'announcement_waiting_sound',
        'sound_file_holding': 'announcement_holding_sound',
        'connexion_mode': 'connection_mode'
    }

    valid_keys_int = {
        'onRealWaitingTime': 'max_waiting_time',
        'onEstimatedWaitingTime': 'max_estimated_waiting_time',
    }

    valid_keys_booleans = {
        'spy_right': 'allow_spy_right',
        'sup_can_record': 'make_record_right',
        'sup_can_consult_record': 'consult_record_right'
    }

    valid_keys_list = ['supervised_profiles', 'supervised_profiles_folders']

    def __init__(self, name, client, project, supervisor_configuration, agent_configuration,
                 folder_ref, profile):
        super(WebAdminSupervisors, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self.name = supervisor_configuration['login']
        self._data = {'email': ''}
        self._data['folder_ref'] = folder_ref
        self._data['profile'] = profile

        self._filter_useful_configuration(supervisor_configuration, agent_configuration)

    def _filter_useful_configuration(self, supervisor_configuration, agent_configuration):
        for key in self.valid_keys_defaults:
            if key in agent_configuration:
                if key == 'lang':
                    self._data[self.valid_keys_defaults[key]] = \
                        format_language(agent_configuration[key])
                else:
                    self._data[self.valid_keys_defaults[key]] = agent_configuration[key]

        for key in self.valid_keys_int:
            if key in agent_configuration:
                self._data[self.valid_keys_int[key]] = int(agent_configuration[key] or 0)

        for key in self.valid_keys_defaults:
            if key in supervisor_configuration:
                self._data[self.valid_keys_defaults[key]] = supervisor_configuration[key]

        for key in self.valid_keys_list:
            if key in supervisor_configuration:
                self._data[key] = supervisor_configuration[key] if supervisor_configuration[key] else []

        for key in self.valid_keys_booleans:
            if key in supervisor_configuration:
                self._data[self.valid_keys_booleans[key]] = bool(supervisor_configuration[key])

        self._data['project'] = self._project.name
        self._data['whitelabel'] = self._whitelabel.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'Supervisor `%s@%s:%s`' % (self.name, self._whitelabel.name, self._project.name)

    @defer.inlineCallbacks
    def compare(self, api_supervisor, transaction):
        if api_supervisor.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_supervisor.config(key):
                    transaction.update_ressource('supervisors', self, api_supervisor)
                    return

            for key in self.list_configuration_keys:
                l1, l2 = self.config(key), api_supervisor.config(key)
                l1.sort(), l2.sort()
                pairs = zip(l1, l2)
                if any(x != y for x, y in pairs):
                    transaction.update_ressource('supervisors', self, api_supervisor)
                    return

                if len(l1) != len(l2):
                    transaction.update_ressource('supervisors', self, api_supervisor)
                    return

            try:
                yield api_supervisor.check_pwds(self.config('password'))

            except:
                transaction.update_ressource('supervisors', self, api_supervisor)
                return

    def update(self, api_supervisor):
        for key in self.configuration_keys:
            api_supervisor.config(key, self.config(key))

        for key in self.list_configuration_keys:
            api_supervisor.config(key, self.config(key))

        for key in self.encrypted_configuration_keys:
            api_supervisor.config(key, self.config(key))

        if api_supervisor.exists():
            return api_supervisor.save()
        else:
            return api_supervisor.create()


class WebAdminProfile(BusinessObject):
    configuration_keys = [
        'initial_channel', 'initial_state',
        'callerid_type', 'callerid_number',
        'outgoing_callerid_type', 'outgoing_callerid_number',
        'outgoing_agent_callerid_type', 'outgoing_agent_callerid_number',
        'inbound_start_popup_url', 'inbound_start_popup_width',
        'inbound_start_popup_height', 'inbound_start_popup_type',
        'inbound_end_popup_url', 'inbound_end_popup_width',
        'inbound_end_popup_height', 'inbound_end_popup_type',
        'outbound_start_popup_url', 'outbound_start_popup_width',
        'outbound_start_popup_height', 'outbound_start_popup_type',
        'outbound_end_popup_url', 'outbound_end_popup_width',
        'outbound_end_popup_height', 'outbound_end_popup_type',
        'max_lost_tasks', 'vocal_max_lost_tasks', 'transfer_targets_folder_id',
        'free_position', 'bypass_wrapup_right', 'make_record_right',
        'cancel_record_right', 'lock_indicators', 'lock_tabs',
        'lock_view_mode', 'activate_extended_mode', 'mailqueues',
        'folder_ref', 'created_at'
    ]

    list_configuration_keys = {
        'tabs': ['index'],  # We can use index only for sorting the list/dict
        'indicators': ['name', 'category'],
        'vocalqueues': ['name'],
    }

    valid_keys_defaults = {
        'default_channel': 'initial_channel',
        'default_state': 'initial_state',
        'callerid_type': 'callerid_type',
        'callerid_freenumber': 'callerid_number',
        "outgoing_callerid_type": 'outgoing_callerid_type',
        "outgoing_callerid_freenumber": 'outgoing_callerid_number',
        "outgoing_agent_callerid_type": 'outgoing_agent_callerid_type',
        "outgoing_agent_callerid_freenumber": 'outgoing_agent_callerid_number',
        'open_URL': 'inbound_start_popup_url',
        'open_TYPE': 'inbound_start_popup_type',
        'close_URL': 'inbound_end_popup_url',
        'close_TYPE': 'inbound_end_popup_type',
        'outgoing_start_URL': 'outbound_start_popup_url',
        'outgoing_start_TYPE': 'outbound_start_popup_type',
        'outgoing_end_URL': 'outbound_end_popup_url',
        'outgoing_end_TYPE': 'outbound_end_popup_type',
        'mail_autowithdrawn_on_lost': 'max_lost_tasks',
        'forcepause_count': 'vocal_max_lost_tasks',
        'target': 'transfer_targets_folder_id',
        'created_at': 'created_at'
    }

    valid_keys_list = {
        'tabs': 'tabs',
        'vocalqueues': 'vocalqueues',
        'mailqueues': 'mailqueues'
    }

    valid_keys_int = {
        'open_W': 'inbound_start_popup_width',
        'open_H': 'inbound_start_popup_height',
        'close_W': 'inbound_end_popup_width',
        'close_H': 'inbound_end_popup_height',
        'outgoing_start_W': 'outbound_start_popup_width',
        'outgoing_start_H': 'outbound_start_popup_height',
        'outgoing_end_W': 'outbound_end_popup_width',
        'outgoing_end_H': 'outbound_end_popup_height',
        'mail_autowithdrawn_on_lost': 'max_lost_tasks',
        'forcepause_count': 'vocal_max_lost_tasks',
    }

    valid_keys_booleans = {
        'allow_free_position': 'free_position',
        'allow_wrapup_bypass': 'bypass_wrapup_right',
        'agent_can_record': 'make_record_right',
        'record_cancel_right': 'cancel_record_right',
        'lock_indicators': 'lock_indicators',
        'lock_urls': 'lock_tabs',
        'lock_view_mode': 'lock_view_mode',
        'extended_view': 'activate_extended_mode'
    }

    callerid_types_translations = {
        'default': 'default',
        'anonymous': 'anonymous',
        'free': 'custom',
        'position': 'position'
    }

    infinite_values = ('mail_autowithdrawn_on_lost', 'forcepause_count')

    def __init__(self, name, client, project, configuration, ppid):
        super(WebAdminProfile, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = {}
        self._data['folder_ref'] = ppid
        self._filter_useful_configuration(configuration)

    def _filter_useful_configuration(self, configuration):
        for value in self.infinite_values:
            if configuration.get(value) == '*':
                configuration[value] = 0

        for key in self.valid_keys_defaults:
            if key in configuration:
                self._data[self.valid_keys_defaults[key]] = configuration[key]

        for key in self.valid_keys_int:
            if key in configuration:
                self._data[self.valid_keys_int[key]] = int(configuration[key] or 0)

        for key in self.valid_keys_list:
            if key in configuration:
                self._data[self.valid_keys_list[key]] = configuration[key] if configuration[key] else []

        for key in self.valid_keys_booleans:
            if key in configuration:
                self._data[self.valid_keys_booleans[key]] = bool(configuration[key])

        self._data['callerid_type'] = self.callerid_types_translations[self._data['callerid_type']]
        self._data['outgoing_callerid_type'] = self.callerid_types_translations[self._data['outgoing_callerid_type']]
        self._data['outgoing_agent_callerid_type'] = self.callerid_types_translations[self._data['outgoing_agent_callerid_type']]

        self._data['indicators'] = self._extract_indicators(configuration)

        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._data['mailqueues'] = []

    def _extract_indicators(self, configuration):
        indicators = []
        if configuration.get('service_indicators'):
            for indicator in configuration['service_indicators'].values():
                indicators.append({'category': 'services', 'name': indicator})

        if configuration.get('session_indicators'):
            for indicator in configuration['session_indicators'].values():
                indicators.append({'category': 'sessions', 'name': indicator})

        return indicators

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'Profile `%s@%s:%s`' % (self.name, self._whitelabel.name,
                                       self._project.name)

    def compare(self, api_profile, transaction):
        if api_profile.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_profile.config(key):
                    transaction.update_ressource('profiles', self, api_profile)
                    return

            for key in self.list_configuration_keys:
                l1, l2 = self.config(key), api_profile.config(key)
                for value in self.list_configuration_keys[key]:
                    l1, l2 = [sorted(l, key=itemgetter(value)) for l in (l1, l2)]

                pairs = zip(l1, l2)
                if any(x != y for x, y in pairs):
                    transaction.update_ressource('profiles', self, api_profile)
                    return

                if len(l1) != len(l2):
                    transaction.update_ressource('profiles', self, api_profile)
                    return

    def update(self, api_profile):
        for key in self.configuration_keys:
            api_profile.config(key, self.config(key))

        for key in self.list_configuration_keys:
            api_profile.config(key, self.config(key))

        if api_profile.exists():
            return api_profile.save()

        else:
            return api_profile.create()


class WebAdminVocalQueue(BusinessObject):
    configuration_keys = [
        'display_name', 'announcement_waiting_sound',
        'announcement_holding_sound', 'max_waiting_time',
        'max_estimated_waiting_time'
        'folder_ref'
    ]

    def __init__(self, name, client, project, configuration):
        super(WebAdminVocalQueue, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'VocalQueue `%s(%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_vocal_queue, transaction):
        if api_vocal_queue.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_vocal_queue.config(key):
                    transaction.update_ressource('vocal_queues', self, api_vocal_queue)
                    break

    def update(self, api_vocal_queue):
        for key in self.configuration_keys:
            api_vocal_queue.config(key, self.config(key))

        if api_vocal_queue.exists():
            return api_vocal_queue.save()

        else:
            return api_vocal_queue.create()


class WebAdminMailQueue(BusinessObject):
    configuration_keys = [
        'name',
        # 'folder_ref'
    ]

    def __init__(self, name, client, project, configuration):
        super(WebAdminMailQueue, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'MailQueue `%s(%s)@%s:%s`' % (
            self.name, self._data.get('name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_mail_queue, transaction):
        if api_mail_queue.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_mail_queue.config(key):
                    transaction.update_ressource('mail_queues', self, api_mail_queue)
                    break

    def update(self, api_mail_queue):
        api_mail_queue.config('name', self.config('name'))
        api_mail_queue.config('folder_ref', self.config('folder_ref'))
        if api_mail_queue.exists():
            return api_mail_queue.save()

        else:
            return api_mail_queue.create()


class WebAdminProfilesFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminProfilesFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'ProfilesFolder `%s(%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_profiles_folder, transaction):
        if not api_profiles_folder.exists():
            return

        if self.name != api_profiles_folder.name:
            transaction.update_ressource(
                'profiles_folders', self, api_profiles_folder)

    def update(self, api_profiles_folder):
        api_profiles_folder.config('name', self.config('name'))
        if api_profiles_folder.exists():
            return api_profiles_folder.save()

        else:
            return api_profiles_folder.create()


class WebAdminQueuesFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminQueuesFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'QueuesFolder `%s (%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_queues_folder, transaction):
        if not api_queues_folder.exists():
            return

        if self.name != api_queues_folder.name:
            transaction.update_queues_folder(
                'queues_folders', self, api_queues_folder)

    def update(self, api_queues_folder):
        api_queues_folder.config('name', self.config('name'))
        if api_queues_folder.exists():
            return api_queues_folder.save()

        else:
            return api_queues_folder.create()


class WebAdminTransferTargetsFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminTransferTargetsFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'TransferTargetsFolder `%s(%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_transfer_targets_folder, transaction):
        if not api_transfer_targets_folder.exists():
            return

        if self.name != api_transfer_targets_folder.name:
            transaction.update_ressource(
                'transfer_targets_folders',
                self, api_transfer_targets_folder)

    def update(self, api_transfer_targets_folder):
        api_transfer_targets_folder.config('name', self.config('name'))
        if api_transfer_targets_folder.exists():
            return api_transfer_targets_folder.save()
        else:
            return api_transfer_targets_folder.create()


class WebAdminTransferTargets(BusinessObject):
    configuration_keys = ['prefix', 'number', 'comment', 'folder_ref']

    def __init__(self, name, client, project, configuration):
        super(WebAdminTransferTargets, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._prefix = self._data['prefix']
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._comment = self._data['comment']
        self._folder_ref = str(self._data['folder_ref'])

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'TransferTarget `(%s)%s[folder_ref:%s]@%s:%s`' % (
            self._data.get('prefix'), self.name, self._folder_ref,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_transfer_target, transaction):
        if not api_transfer_target.exists():
            return

        if self.name != api_transfer_target.name or \
                self.config('prefix') != api_transfer_target.config('prefix') or \
                (api_transfer_target.config('folder_ref') is not None and
                self.config('folder_ref') != api_transfer_target.config('folder_ref')) or \
                self.config('comment') != api_transfer_target.config('comment') or \
                self.config('transferplus_number') != api_transfer_target.config('transferplus_number'):
            transaction.update_ressource('transfer_targets', self, api_transfer_target)

    def update(self, api_transfer_target):
        api_transfer_target.config('number', self.config('number'))
        api_transfer_target.config('prefix', self.config('prefix'))
        api_transfer_target.config('comment', self.config('comment'))
        api_transfer_target.config('folder_ref', self.config('folder_ref'))
        api_transfer_target.config('transferplus_number', self.config('transferplus_number'))
        if api_transfer_target.exists():
            return api_transfer_target.save()
        else:
            return api_transfer_target.create()


class WebAdminPositionsFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminPositionsFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'PositionsFolder `%s(%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_positions_folder, transaction):
        if not api_positions_folder.exists():
            return

        if self.name != api_positions_folder.name:
            transaction.update_ressource(
                'positions_folders',
                self, api_positions_folder)

    def update(self, api_positions_folder):
        api_positions_folder.config('name', self.config('name'))
        if api_positions_folder.exists():
            return api_positions_folder.save()
        else:
            return api_positions_folder.create()


class WebAdminPositions(BusinessObject):
    configuration_keys = ['prefix', 'number', 'comment', 'folder_ref', 'position']

    def __init__(self, name, client, project, configuration):
        super(WebAdminPositions, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._prefix = self._data['prefix']
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._comment = self._data['comment']
        self._folder_ref = str(self._data['folder_ref'])
        self._position = str(self._data['position'])

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'Position `(%s)%s[position:%s, folder_ref:%s]@%s:%s`' % (
            self._data.get('prefix'), self.name,
            self._position, self._folder_ref,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_position, transaction):
        if api_position.exists():
            for key in self.configuration_keys:
                if self.config(key) != api_position.config(key):
                    transaction.update_ressource('positions', self, api_position)
                    return

    def update(self, api_position):
        for key in self.configuration_keys:
            api_position.config(key, self.config(key))

        if api_position.exists():
            return api_position.save()
        else:
            return api_position.create()


class WebAdminCalendars(BusinessObject):
    configuration_keys = ['parent_name', 'name']

    def __init__(self, name, client, project, old_id, configuration):
        super(WebAdminCalendars, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_name = str(self._data['parent_name'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self.old_id = old_id

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'Calendars `%s(parent_name: %s)@%s:%s`' % (
            self.name, self._parent_name,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_calendar, transaction):
        if not api_calendar.exists():
            return

    def update(self, api_calendar):
        api_calendar.config('name', self.config('name'))
        if api_calendar.exists():
            return api_calendar.save()
        else:
            return api_calendar.create()


class WebAdminSpecialDays(BusinessObject):
    configuration_keys = ['calendar_name', 'start_date', 'end_date']

    def __init__(self, client, project, configuration):
        super(WebAdminSpecialDays, self).__init__('', client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._start_date = self._data['start_date']
        self._end_date = self._data['end_date']
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._calendar_name = str(self._data['calendar_name'])

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'SpecialDay `[start_date:%s, end_date: %s, calendar_name:%s]@%s:%s`' % (
            self._start_date, self._end_date, self._calendar_name,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_specialday, transaction):
        if not api_specialday.exists():
            return

    def update(self, api_specialday):
        for key in self.configuration_keys:
            api_specialday.config(key, self.config(key))

        if api_specialday.exists():
            return api_specialday.save()
        else:
            return api_specialday.create()


class WebAdminScenariosFolders(BusinessObject):
    configuration_keys = ['id', 'parent_id', 'name']

    def __init__(self, name, client, project, configuration):
        super(WebAdminScenariosFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_id = str(self._data['parent_id'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'ScenariosFolder `%s(%s)@%s:%s`' % (
            self.name, self._data.get('display_name'),
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_scenarios_folder, transaction):
        if not api_scenarios_folder.exists():
            return

        if self.name != api_scenarios_folder.name:
            transaction.update_ressource(
                'scenarios_folders',
                self, api_scenarios_folder)

    def update(self, api_scenarios_folder):
        api_scenarios_folder.config('name', self.config('name'))
        if api_scenarios_folder.exists():
            return api_scenarios_folder.save()
        else:
            return api_scenarios_folder.create()


class WebAdminScenarios(BusinessObject):
    configuration_keys = ['name', 'folder_name', 'folder_ref']

    def __init__(self, name, client, project, configuration):
        super(WebAdminScenarios, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._folder_name = str(self._data['folder_name'])

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'Scenario `[scenario:%s, folder_name:%s]@%s:%s`' % (
            self.name, self._folder_name,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_scenario, transaction):
        if api_scenario.exists():
            return

    def update(self, api_scenario):
        for key in self.configuration_keys:
            api_scenario.config(key, self.config(key))

        if api_scenario.exists():
            return api_scenario.save()
        else:
            return api_scenario.create()


class WebAdminEntryPoints(BusinessObject):
    configuration_keys = ['primary_data', 'auxiliary_data', 'sub_type',
                          'description', 'scenario', 'type']

    def __init__(self, name, client, project, configuration):
        super(WebAdminEntryPoints, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._type = str(self._data['type'])

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'EntryPoints `[entrypoint:%s, type:%s]@%s:%s`' % (
            self.name, self._type,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_scenario, transaction):
        if api_scenario.exists():
            return

    def update(self, api_scenario):
        for key in self.configuration_keys:
            api_scenario.config(key, self.config(key))

        if api_scenario.exists():
            return api_scenario.save()
        else:
            return api_scenario.create()


class WebAdminSoundFilesFolders(BusinessObject):
    configuration_keys = ['parent_name', 'name']

    def __init__(self, name, client, project, old_id, configuration):
        super(WebAdminSoundFilesFolders, self).__init__(name, client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._parent_name = str(self._data['parent_name'])
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self.old_id = old_id

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'SoundFiles Folders `%s(parent_name: %s)@%s:%s`' % (
            self.name, self._parent_name,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_soundfilesfolder, transaction):
        if not api_soundfilesfolder.exists():
            return

    def update(self, api_soundfilesfolder):
        api_soundfilesfolder.config('name', self.config('name'))
        if api_soundfilesfolder.exists():
            return api_soundfilesfolder.save()
        else:
            return api_soundfilesfolder.create()


class WebAdminSoundFiles(BusinessObject):
    configuration_keys = ['folder_name', 'created_at', 'url', 'metadata']

    def __init__(self, client, project, old_id, configuration):
        super(WebAdminSoundFiles, self).__init__('', client)
        self._project = project
        self._whitelabel = project._whitelabel
        self._data = configuration
        self._data['whitelabel'] = self._whitelabel.name
        self._data['project'] = self._project.name
        self._folder_name = str(self._data['folder_name'])
        self.old_id = old_id

    def config(self, key):
        return self._data.get(key)

    def __str__(self):
        return 'SoundFile `[display_name:%s, file_id: %s, folder_name:%s]@%s:%s`' % (
            self.config('display_name'), self.config('path'), self._folder_name,
            self._whitelabel.name, self._project.name
        )

    def compare(self, api_soundfile, transaction):
        if not api_soundfile.exists():
            return

    def update(self, api_soundfile):
        for key in self.configuration_keys:
            api_soundfile.config(key, self.config(key))

        if api_soundfile.exists():
            return api_soundfile.save()
        else:
            return api_soundfile.create()
