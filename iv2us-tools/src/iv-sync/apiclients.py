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

from datetime import datetime, time
from ivsync.collectionobjects import (
    APIAgent,
    APISupervisor,
    APIProfile,
    APIProject,
    APITransferTarget,
    APITransferTargetsFolder,
    APIQueuesFolder,
    APIMailQueue,
    APIVocalQueue,
    APIWhitelabel,
    APIProfilesFolder,
    APIPositionsFolder,
    APIPosition,
    APIAgentsFolder,
    APISupervisorsFolder,
    APICalendar,
    APISpecialDay,
    APIScenariosFolder,
    APIScenario,
    APIEntryPoint,
    APISoundFilesFolder,
    APISoundFile
)
from ivsync.utils import Client
from ivcommons.apiclients import ConfigurationAPIClient
from twisted.python import log


class ConfigApiClient(Client):
    def _parse_credentials(self, args):
        self._host = args.api_host
        self._port = args.api_port
        self._use_ssl = not args.api_no_ssl
        self._overlord_key = args.api_key

    def _initialise_client(self):
        log.msg("Initialising API client.")
        self._client = ConfigurationAPIClient(
            self._overlord_key, self._host,
            self._port, self._use_ssl
        )

    def _test(self):
        log.msg("Testing API connectivity.")

        d = self._client.whitelabels.read_all()  # pylint: disable=E1101
        d.chainDeferred(self.ready_deferred)

    def _test_success_msg(self):
        return "Connectivity test to API succeeded!"

    def get_whitelabel(self, whitelabel):
        d = self._client.whitelabels.read_one(whitelabel.name)  # pylint: disable=E1101

        def build_object(_):
            return APIWhitelabel(whitelabel.name, self)

        def failure_is_not_an_option(_):
            return APIWhitelabel(whitelabel.name, self, exists=False)

        d.addCallbacks(build_object, failure_is_not_an_option)
        return d

    def get_project(self, project):
        d = self._client.projects.read_one(  # pylint: disable=E1101
            project.name,
            whitelabel=project._whitelabel.name
        )

        def build_object(_):
            return APIProject(project.name, project._whitelabel.name, self)

        def failure_is_not_an_option(_):
            return APIProject(
                project.name, project._whitelabel.name, self,
                exists=False
            )

        d.addCallbacks(build_object, failure_is_not_an_option)
        return d

    def get_profile(self, profile):
        d = self._client.profiles.read_one(  # pylint: disable=E1101
            profile.name,
            whitelabel=profile._whitelabel.name,
            project=profile._project.name
        )

        def build_object(api_config, profile):
            # Because default read field...
            api_config.pop('users_count')
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0

            return APIProfile(
                profile.name,
                profile._project.name, profile._whitelabel.name, self, api_config
            )

        def failure_is_not_an_option(_, profile):
            return APIProfile(
                profile.name,
                profile._project.name, profile._whitelabel.name, self,
                profile._data, exists=False
            )

        d.addCallbacks(
            build_object, failure_is_not_an_option,
            callbackArgs=(profile,),
            errbackArgs=(profile,)
        )
        return d

    def get_agent(self, agent):
        d = self._client.users.read_one(  # pylint: disable=E1101
            agent.name,
            whitelabel=agent._whitelabel.name,
            project=agent._project.name
        )

        def build_object(api_config, agent):
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0

            return APIAgent(
                agent.name,
                agent._project.name, agent._whitelabel.name, agent._profile,
                self, api_config
            )

        def failure_is_not_an_option(_, agent):
            return APIAgent(
                agent.name,
                agent._project.name, agent._whitelabel.name, agent._profile,
                self, agent._data, exists=False
            )

        d.addCallbacks(
            build_object, failure_is_not_an_option,
            callbackArgs=(agent,),
            errbackArgs=(agent,)
        )
        return d

    def get_agents_folder(self, agents_folder):
        d = self._client.usersfolders.read_one(  # pylint: disable=E1101
            agents_folder.name,
            whitelabel=agents_folder._whitelabel.name,
            project=agents_folder._project.name,
            parent_id=agents_folder._parent_id,
            type='agent'
        )

        def build_object(api_config, agent):
            return APIAgentsFolder(
                agents_folder.name,
                agents_folder._whitelabel.name,
                agents_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, agents_folder):
            return APIAgentsFolder(
                agents_folder.name,
                agents_folder._whitelabel.name,
                agents_folder._project.name,
                self,
                agents_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(agents_folder,),
            errbackArgs=(agents_folder,)
        )
        return d

    def get_supervisors_folder(self, supervisors_folder):
        d = self._client.usersfolders.read_one(  # pylint: disable=E1101
            supervisors_folder.name,
            whitelabel=supervisors_folder._whitelabel.name,
            project=supervisors_folder._project.name,
            parent_id=supervisors_folder._parent_id,
            type='supervisor'
        )

        def build_object(api_config, agent):
            return APISupervisorsFolder(
                supervisors_folder.name,
                supervisors_folder._whitelabel.name,
                supervisors_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, supervisors_folder):
            return APISupervisorsFolder(
                supervisors_folder.name,
                supervisors_folder._whitelabel.name,
                supervisors_folder._project.name,
                self,
                supervisors_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(supervisors_folder,),
            errbackArgs=(supervisors_folder,)
        )
        return d

    def get_supervisor(self, supervisor):
        d = self._client.users.read_one(  # pylint: disable=E1101
            supervisor.name,
            whitelabel=supervisor._whitelabel.name,
            project=supervisor._project.name
        )

        def build_object(api_config, supervisor):
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0
            api_config['supervised_profiles'] = [x['name'] for x in api_config['supervised_profiles']]
            api_config['supervised_profiles_folders'] = [x['id'] for x in api_config['supervised_profiles_folders']]

            return APISupervisor(
                supervisor.name,
                supervisor._project.name,
                supervisor._whitelabel.name,
                self, api_config
            )

        def failure_is_not_an_option(_, supervisor):
            return APISupervisor(
                supervisor.name,
                supervisor._project.name,
                supervisor._whitelabel.name,
                self, supervisor._data, exists=False
            )

        d.addCallbacks(
            build_object, failure_is_not_an_option,
            callbackArgs=(supervisor,),
            errbackArgs=(supervisor,)
        )
        return d

    def get_queues_folder(self, queues_folder):
        d = self._client.queuesfolders.read_one(  # pylint: disable=E1101
            queues_folder.name,
            whitelabel=queues_folder._whitelabel.name,
            project=queues_folder._project.name,
            parent_id=queues_folder._parent_id
        )

        def build_object(api_config, _):
            return APIQueuesFolder(
                queues_folder.name,
                queues_folder._whitelabel.name,
                queues_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, a):
            return APIQueuesFolder(
                queues_folder.name,
                queues_folder._whitelabel.name,
                queues_folder._project.name,
                self,
                queues_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(queues_folder,),
            errbackArgs=(queues_folder,)
        )
        return d

    def get_vocal_queue(self, vocal_queue):
        d = self._client.vocalqueues.read_one(  # pylint: disable=E1101
            vocal_queue.name,
            whitelabel=vocal_queue._whitelabel.name,
            project=vocal_queue._project.name
        )

        def build_object(api_config, agent):
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0

            return APIVocalQueue(
                vocal_queue.name,
                vocal_queue._whitelabel.name,
                vocal_queue._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, vocal_queue):
            return APIVocalQueue(
                vocal_queue.name,
                vocal_queue._whitelabel.name,
                vocal_queue._project.name,
                self,
                vocal_queue._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(vocal_queue,),
            errbackArgs=(vocal_queue,)
        )
        return d

    def get_mail_queue(self, mail_queue):
        d = self._client.mailqueues.read_one(  # pylint: disable=E1101
            mail_queue.name,
            whitelabel=mail_queue._whitelabel.name,
            project=mail_queue._project.name
        )

        def build_object(api_config, agent):
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0

            return APIMailQueue(
                mail_queue.name,
                mail_queue._whitelabel.name,
                mail_queue._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, mail_queue):
            return APIMailQueue(
                mail_queue.name,
                mail_queue._whitelabel.name,
                mail_queue._project.name,
                self,
                mail_queue._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(mail_queue,),
            errbackArgs=(mail_queue,)
        )
        return d

    def get_profiles_folder(self, profiles_folder):
        d = self._client.profilesfolders.read_one(  # pylint: disable=E1101
            profiles_folder.name,
            whitelabel=profiles_folder._whitelabel.name,
            project=profiles_folder._project.name,
            parent_id=profiles_folder._parent_id
        )

        def build_object(api_config, agent):
            return APIProfilesFolder(
                profiles_folder.name,
                profiles_folder._whitelabel.name,
                profiles_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, profiles_folder):
            return APIProfilesFolder(
                profiles_folder.name,
                profiles_folder._whitelabel.name,
                profiles_folder._project.name,
                self,
                profiles_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(profiles_folder,),
            errbackArgs=(profiles_folder,)
        )
        return d

    def get_transfer_targets_folder(self, transfer_targets_folder):
        d = self._client.transfertargetsfolders.read_one(  # pylint: disable=E1101
            transfer_targets_folder.name,
            whitelabel=transfer_targets_folder._whitelabel.name,
            project=transfer_targets_folder._project.name,
            parent_id=transfer_targets_folder._parent_id
        )

        def build_object(api_config, agent):
            return APITransferTargetsFolder(
                transfer_targets_folder.name,
                transfer_targets_folder._whitelabel.name,
                transfer_targets_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, transfer_targets_folder):
            return APITransferTargetsFolder(
                transfer_targets_folder.name,
                transfer_targets_folder._whitelabel.name,
                transfer_targets_folder._project.name,
                self,
                transfer_targets_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(transfer_targets_folder,),
            errbackArgs=(transfer_targets_folder,)
        )
        return d

    def get_transfer_target(self, transfer_target):
        d = self._client.transfertargets.read_one(  # pylint: disable=E1101
            transfer_target.name,
            whitelabel=transfer_target._whitelabel.name,
            project=transfer_target._project.name,
            folder_ref=transfer_target._folder_ref,
            prefix=transfer_target._prefix,
            comment=transfer_target._comment
        )

        def build_object(api_config, agent):
            if api_config.get('transferplus_number') is None:
                api_config['transferplus_number'] = ""

            return APITransferTarget(
                transfer_target.name,
                transfer_target._whitelabel.name,
                transfer_target._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, transfer_target):
            return APITransferTarget(
                transfer_target.name,
                transfer_target._whitelabel.name,
                transfer_target._project.name,
                self,
                transfer_target._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(transfer_target,),
            errbackArgs=(transfer_target,)
        )
        return d

    def get_positions_folder(self, positions_folder):
        d = self._client.positionsfolders.read_one(  # pylint: disable=E1101
            positions_folder.name,
            whitelabel=positions_folder._whitelabel.name,
            project=positions_folder._project.name,
            parent_id=positions_folder._parent_id
        )

        def build_object(api_config, agent):
            return APIPositionsFolder(
                positions_folder.name,
                positions_folder._whitelabel.name,
                positions_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, positions_folder):
            return APIPositionsFolder(
                positions_folder.name,
                positions_folder._whitelabel.name,
                positions_folder._project.name,
                self,
                positions_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(positions_folder,),
            errbackArgs=(positions_folder,)
        )
        return d

    def get_position(self, position):
        d = self._client.positions.read_one(  # pylint: disable=E1101
            position.name,
            whitelabel=position._whitelabel.name,
            project=position._project.name,
            position=position._position
        )

        def build_object(api_config, agent):
            if api_config.get('folder_ref') is None:
                api_config['folder_ref'] = 0

            return APIPosition(
                position.name,
                position._whitelabel.name,
                position._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, position):
            return APIPosition(
                position.name,
                position._whitelabel.name,
                position._project.name,
                self,
                position._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(position,),
            errbackArgs=(position,)
        )
        return d

    def get_calendar(self, calendar):
        d = self._client.calendars.read_all(  # pylint: disable=E1101
            whitelabel=calendar._whitelabel.name,
            project=calendar._project.name,
        )

        def build_object(api_config, _):
            parent_id = 0
            to_create = True
            for _calendar in api_config:
                if _calendar['name'] == calendar.config('parent_name'):
                    parent_id = _calendar['id']

                if _calendar['name'] == calendar.name:
                    to_create = False

            if to_create:
                return APICalendar(
                    calendar.name,
                    calendar._whitelabel.name,
                    calendar._project.name,
                    self,
                    calendar._client,
                    calendar.old_id,
                    config={'parent_id': parent_id},
                    exists=False
                )

            else:
                return APICalendar(
                    calendar.name,
                    calendar._whitelabel.name,
                    calendar._project.name,
                    self,
                    calendar._client,
                    calendar.old_id,
                    config={'parent_id': parent_id},
                    exists=True
                )

        def failure_is_not_an_option(_, calendar):
            return APICalendar(
                calendar.name,
                calendar._whitelabel.name,
                calendar._project.name,
                self,
                calendar._client,
                calendar.old_id,
                config={'parent_id': 0},
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(calendar,),
            errbackArgs=(calendar,)
        )
        return d

    def get_specialday(self, specialday):
        d = self._client.calendars.read_all(  # pylint: disable=E1101
            whitelabel=specialday._whitelabel.name,
            project=specialday._project.name,
        )

        def build_object(api_config, agent):
            calendar_id = 0
            to_create = True
            for calendar in api_config:
                if calendar['name'] == specialday.config("calendar_name"):
                    calendar_id = calendar['id']
                    for _specialday in calendar['special_days']:
                        if _specialday['start_date'] == str(specialday.config('start_date')):
                            if specialday.config('end_date') is None:
                                end_date = str(datetime.combine(
                                    datetime.strptime(str(specialday.config('start_date')), '%Y-%m-%d %H:%M:%S'),
                                    time(23, 59, 59)
                                ))
                            else:
                                end_date = str(specialday.config('end_date'))

                            if _specialday['end_date'] == end_date:
                                to_create = False

            # Only create and ignore specialdays on root
            if to_create and calendar_id:
                return APISpecialDay(
                    "%s//%s :: %s" % (specialday.config('start_date'), specialday.config('end_date'), specialday.config("calendar_name")),
                    specialday._whitelabel.name,
                    specialday._project.name,
                    self,
                    {
                        'calendar_id': calendar_id,
                        'calendar_name': specialday.config("calendar_name"),
                        'start_date': str(specialday.config('start_date')),
                        'end_date': str(specialday.config('end_date')),
                        'updated_at': str(specialday.config('updated_at'))
                    },
                    exists=False
                )

            else:
                return APISpecialDay(
                    "%s//%s :: %s" % (specialday.config('start_date'), specialday.config('end_date'), specialday.config("calendar_name")),
                    specialday._whitelabel.name,
                    specialday._project.name,
                    self,
                    {
                        'calendar_id': calendar_id,
                        'calendar_name': specialday.config("calendar_name"),
                        'start_date': str(specialday.config('start_date')),
                        'end_date': str(specialday.config('end_date')),
                        'updated_at': str(specialday.config('updated_at'))
                    },
                    exists=True
                )

        d.addCallback(build_object, specialday)
        return d

    def get_scenarios_folder(self, scenarios_folder):
        d = self._client.scenariosfolders.read_one(  # pylint: disable=E1101
            scenarios_folder.name,
            whitelabel=scenarios_folder._whitelabel.name,
            project=scenarios_folder._project.name,
            parent_id=scenarios_folder._parent_id
        )

        def build_object(api_config, agent):
            return APIScenariosFolder(
                scenarios_folder.name,
                scenarios_folder._whitelabel.name,
                scenarios_folder._project.name,
                self,
                api_config
            )

        def failure_is_not_an_option(_, positions_folder):
            return APIScenariosFolder(
                scenarios_folder.name,
                scenarios_folder._whitelabel.name,
                scenarios_folder._project.name,
                self,
                scenarios_folder._data,
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(scenarios_folder,),
            errbackArgs=(scenarios_folder,)
        )
        return d

    def get_scenario(self, scenario):
        d = self._client.scenarios.read_all(  # pylint: disable=E1101
            whitelabel=scenario._whitelabel.name,
            project=scenario._project.name,
            type='vocal',
            name=scenario.name
        )

        def build_object(api_config, _):
            if api_config[0].get('folder_ref') is None:
                api_config[0]['folder_ref'] = 0

            return APIScenario(
                scenario.name,
                scenario._whitelabel.name,
                scenario._project.name,
                self,
                {
                    'name': scenario.name,
                    'type': 'vocal',
                    'folder_ref': scenario.config('folder_ref'),
                    'updated_at': str(scenario.config('updated_at'))
                }
            )

        def failure_is_not_an_option(_, scenario):
            return APIScenario(
                scenario.name,
                scenario._whitelabel.name,
                scenario._project.name,
                self,
                {
                    'name': scenario.name,
                    'type': 'vocal',
                    'folder_ref': scenario.config('folder_ref'),
                    'updated_at': str(scenario.config('updated_at'))
                },
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(scenario,),
            errbackArgs=(scenario,)
        )
        return d

    def get_entrypoint(self, entrypoint):
        d = self._client.entrypoints.read_all(  # pylint: disable=E1101
            whitelabel=entrypoint._whitelabel.name,
            project=entrypoint._project.name,
        )

        def build_object(api_config, _):
            to_create = True
            for _entrypoint in api_config:
                if _entrypoint['primary_data'] == entrypoint.name:
                    to_create = False

            if to_create:
                return APIEntryPoint(
                    entrypoint.name,
                    entrypoint._whitelabel.name,
                    entrypoint._project.name,
                    self,
                    {
                        'primary_data': entrypoint.config("primary_data"),
                        'auxiliary_data': entrypoint.config("auxiliary_data"),
                        'type': entrypoint.config("type"),
                        'sub_type': entrypoint.config("sub_type"),
                        'description': entrypoint.config("description"),
                        'updated_at': str(entrypoint.config('updated_at')),
                        'scenario': entrypoint.config('scenario')
                    },
                    exists=False
                )
            else:
                return APIEntryPoint(
                    entrypoint.name,
                    entrypoint._whitelabel.name,
                    entrypoint._project.name,
                    self,
                    {
                        'primary_data': entrypoint.config("primary_data"),
                        'auxiliary_data': entrypoint.config("auxiliary_data"),
                        'type': entrypoint.config("type"),
                        'sub_type': entrypoint.config("sub_type"),
                        'description': entrypoint.config("description"),
                        'updated_at': str(entrypoint.config('updated_at')),
                        'scenario': entrypoint.config('scenario')
                    },
                    exists=True
                )

        def failure_is_not_an_option(_, entrypoint):
            return APIEntryPoint(
                entrypoint.name,
                entrypoint._whitelabel.name,
                entrypoint._project.name,
                self,
                {
                    'primary_data': entrypoint.config("primary_data"),
                    'auxiliary_data': entrypoint.config("auxiliary_data"),
                    'type': entrypoint.config("type"),
                    'sub_type': entrypoint.config("sub_type"),
                    'description': entrypoint.config("description"),
                    'updated_at': str(entrypoint.config('updated_at')),
                    'scenario': entrypoint.config('scenario')
                },
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(entrypoint,),
            errbackArgs=(entrypoint,)
        )
        return d

    def get_soundfiles_folder(self, folder):
        d = self._client.soundfilesfolders.read_all(  # pylint: disable=E1101
            whitelabel=folder._whitelabel.name,
            project=folder._project.name,
        )

        def build_object(api_config, _):
            parent_id = 0
            to_create = True
            for _folder in api_config:
                if _folder['name'] == folder.config('parent_name'):
                    parent_id = _folder['id']

                if _folder['name'] == folder.name:
                    to_create = False

            if to_create:
                return APISoundFilesFolder(
                    folder.name,
                    folder._whitelabel.name,
                    folder._project.name,
                    self,
                    folder.old_id,
                    config={'parent_id': parent_id},
                    exists=False
                )

            else:
                return APISoundFilesFolder(
                    folder.name,
                    folder._whitelabel.name,
                    folder._project.name,
                    self,
                    folder.old_id,
                    config={'parent_id': parent_id},
                    exists=True
                )

        def failure_is_not_an_option(_, folder):
            return APISoundFilesFolder(
                folder.name,
                folder._whitelabel.name,
                folder._project.name,
                self,
                folder.old_id,
                config={'parent_id': 0},
                exists=False
            )

        d.addCallbacks(
            build_object,
            failure_is_not_an_option,
            callbackArgs=(folder,),
            errbackArgs=(folder,)
        )
        return d

    def get_soundfile(self, soundfile):
        d = self._client.soundfilesfolders.read_all(  # pylint: disable=E1101
            whitelabel=soundfile._whitelabel.name,
            project=soundfile._project.name,
        )

        def build_object(api_config, agent):
            folder_id = 0
            to_create = True
            for folder in api_config:
                if folder['name'] == soundfile.config("folder_name"):
                    folder_id = folder['id']
                    to_create = True

            # Only create and ignore soundfiles on root
            if to_create:
                return APISoundFile(
                    soundfile.config('display_name'),
                    soundfile._whitelabel.name,
                    soundfile._project.name,
                    self,
                    soundfile._client,
                    soundfile.old_id,
                    {
                        'folder_id': folder_id,
                        'folder_name': soundfile.config("folder_name"),
                        'display_name': str(soundfile.config('display_name')),
                        'type': str(soundfile.config('type')),
                        'path': str(soundfile.config('path')),
                        'url': soundfile.config('url'),
                        'metadata': soundfile.config('metadata'),
                        'created_at': soundfile.config('created_at')
                    },
                    False
                )

            else:
                return APISoundFile(
                    soundfile.config('display_name'),
                    soundfile._whitelabel.name,
                    soundfile._project.name,
                    self,
                    soundfile._client,
                    soundfile.old_id,
                    {
                        'folder_id': folder_id,
                        'folder_name': soundfile.config("folder_name"),
                        'display_name': str(soundfile.config('display_name')),
                        'type': str(soundfile.config('type')),
                        'path': str(soundfile.config('path')),
                        'url': soundfile.config('url'),
                        'metadata': soundfile.config('metadata'),
                        'created_at': soundfile.config('created_at')
                    },
                    True
                )

        d.addCallback(build_object, soundfile)
        return d
