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

from trest import TrestNoContent, TrestConflict

from ivsync.utils import BusinessObject
from ivsync import utils

from twisted.internet import defer, reactor, stdio
from twisted.python import log

ERRORS = {}


class APIBusinessObject(BusinessObject):
    def __init__(self, name, client, exists=True):
        super(APIBusinessObject, self).__init__(name, client)
        self._exists = exists

    def exists(self):
        return self._exists

    def failed(self, failure, action):
        if isinstance(failure.value, TrestNoContent):
            if utils.RETURN_CODE < 1:
                utils.RETURN_CODE = 1
        else:
            if utils.RETURN_CODE < 2:
                utils.RETURN_CODE = 2

        log.msg(
            "Action [%s] failed for %s: %s" %
            (action, self, str(failure.value))
        )
        tag = str(self).split('@')[1]
        ressource = str(self).split('@')[0].split(' ')[0]
        ERRORS.setdefault(tag, {})[(ressource, action)] = ERRORS.setdefault(
            tag, {}).get((ressource, action), 0) + 1


class APIWhitelabel(APIBusinessObject):
    def __str__(self):
        return "Whitelabel `%s'" % (self.name,)

    def create(self):
        return self._client._client.whitelabels.create(name=self.name)


class APIProject(APIBusinessObject):
    def __init__(self, name, whitelabel, client, exists=True):
        super(APIProject, self).__init__(name, client, exists)
        self._whitelabel = whitelabel

    def __str__(self):
        return "Project `%s:%s'" % (self._whitelabel, self.name)

    def create(self):
        return self._client._client.projects.create(
            name=self.name,
            whitelabel=self._whitelabel
        )


class APIRessource(APIBusinessObject):
    def __init__(self, name, project, whitelabel, client, config={},
                 exists=True):
        super(APIRessource, self).__init__(name, client, exists)
        self._whitelabel = whitelabel
        self._project = project
        self._config = config
        self._config['whitelabel'] = self._whitelabel
        self._config['project'] = self._project
        self._res_name = None
        self._name = self.name
        self._collection = None

    def __str__(self):
        return "%s `%s@%s:%s'" % (
            self._res_name, self._name, self._whitelabel, self._project
        )

    def config(self, key, value=None):
        if value is not None:
            self._config[key] = value

        else:
            return self._config.get(key)

    def save(self):
        log.msg("Updating %s in ConfigurationAPI." % (self,))
        return self._collection.update_one(
            self.name, **self._config
        ).addErrback(self.failed, "update")

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._collection.create(
            name=self.name, **self._config
        ).addErrback(self.failed, "create")


class APIProfile(APIRessource):
    def __init__(self, name, project, whitelabel, client, config={},
                 exists=True):
        super(APIProfile, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._res_name = "Profile"
        self._collection = self._client._client.profiles


class APIAgent(APIRessource):
    def __init__(self, name, project, whitelabel, profile, client, config={},
                 exists=True):
        super(APIAgent, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._res_name = "Agent"
        self._collection = self._client._client.users
        self._profile = profile

    def check_pwds(self, password, phone_password):
        return self._collection.read_one(  # pylint: disable=E1101
            self.name,
            whitelabel=self._whitelabel,
            project=self._project,
            password=password,
            phone_password=phone_password
        )

    def save(self):
        log.msg("Updating %s in ConfigurationAPI." % (self,))
        self._config['profile'] = self._profile
        self._config['type'] = 'agent'
        for key in self._config.keys():
            if self._config[key] is None:
                del self._config[key]

        return self._client._client.users.update_one(
            self.name, **self._config
        ).addErrback(self.failed, "update")

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        self._config['profile'] = self._profile
        self._config['type'] = 'agent'
        for key in self._config.keys():
            if self._config[key] is None:
                del self._config[key]

        return self._client._client.users.create(
            **self._config
        ).addErrback(self.failed, "create")


class APIAgentsFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIAgentsFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.usersfolders

    def __str__(self):
        return "AgentsFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )

    def save(self):
        log.msg("Updating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'agent'
        return self._collection.update_one(
            self.name, **self._config
        ).addErrback(self.failed, "update")

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'agent'
        return self._collection.create(
            name=self.name, **self._config
        ).addErrback(self.failed, "create")


class APISupervisorsFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APISupervisorsFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.usersfolders

    def __str__(self):
        return "SupervisorsFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )

    def save(self):
        log.msg("Updating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'supervisor'
        return self._collection.update_one(
            self.name, **self._config
        ).addErrback(self.failed, "update")

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'supervisor'
        return self._collection.create(
            name=self.name, **self._config
        ).addErrback(self.failed, "create")


class APISupervisor(APIRessource):
    def __init__(self, name, project, whitelabel, client, config={}, exists=True):
        super(APISupervisor, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._res_name = "Supervisor"
        self._collection = self._client._client.users

    def check_pwds(self, password):
        return self._collection.read_one(  # pylint: disable=E1101
            self.name,
            whitelabel=self._whitelabel,
            project=self._project,
            password=password,
        )

    def save(self):
        log.msg("Updating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'supervisor'
        for key in self._config.keys():
            if self._config[key] is None:
                del self._config[key]

        return self._client._client.users.update_one(
            self.name, **self._config
        ).addErrback(self.failed, "update")

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        self._config['type'] = 'supervisor'
        for key in self._config.keys():
            if self._config[key] is None:
                del self._config[key]

        return self._client._client.users.create(
            **self._config
        ).addErrback(self.failed, "create")


class APIQueuesFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIQueuesFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.queuesfolders

    def __str__(self):
        return "QueuesFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )


class APIVocalQueue(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIVocalQueue, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._res_name = "VocalQueue"
        self._name = self._config['display_name']
        self._collection = self._client._client.vocalqueues


class APIMailQueue(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIMailQueue, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._res_name = self._config['name']
        self._name = self.name
        self._collection = self._client._client.mailqueues

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._collection.create(
            **self._config
        ).addErrback(self.failed, "create")


class APIProfilesFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIProfilesFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.profilesfolders

    def __str__(self):
        return "ProfilesFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )


class APITransferTargetsFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APITransferTargetsFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.transfertargetsfolders

    def __str__(self):
        return "TransferTargetsFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )


class APITransferTarget(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APITransferTarget, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.transfertargets
        self._old_config = {
            'number': name,
            'prefix': config['prefix'],
            'comment': config['comment'],
            'transferplus_number': config['transferplus_number'],
            'whitelabel': self._whitelabel,
            'project': self._project
        }

    def __str__(self):
        return "TransferTarget `(%s)%s[folder_ref:%s]@%s:%s`" % (
            self._config['prefix'], self.name, self._config.get('folder_ref'),
            self._whitelabel, self._project
        )

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._client._client.transfertargets.create(
            number=self.name, **self._config
        ).addErrback(self.failed, "create")

    def save(self):
        log.msg("Updating[1/2]: Deleting %s in ConfigurationAPI" % (self))

        def create(_):
            log.msg("Updating[2/2]: Creating %s in ConfigurationAPI" % (self))
            d = self._client._client.transfertargets.create(
                **self._config
            )
            d.addErrback(self.failed, "update")
            return d

        d = self._client._client.transfertargets.delete_one(
            self.name, **self._old_config
        )
        d.addCallbacks(create, self.failed, errbackArgs=['update'])
        return d


class APIPositionsFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIPositionsFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.positionsfolders

    def __str__(self):
        return "PositionsFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )


class APIPosition(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIPosition, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.positions
        self._old_config = {
            'number': name,
            'prefix': config['prefix'],
            'comment': config['comment'],
            'position': config['position'],
            'whitelabel': self._whitelabel,
            'project': self._project
        }

    def __str__(self):
        return "Position `(%s)%s[position:%s, folder_ref:%s]@%s:%s`" % (
            self._config['prefix'], self.name, self._config.get('position', 'no_position'),
            self._config.get('folder_ref'),
            self._whitelabel, self._project
        )

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._client._client.positions.create(
            **self._config
        ).addErrback(self.failed, "create")

    def save(self):
        log.msg("Updating[1/2]: Deleting %s in ConfigurationAPI" % (self))

        def create(_):
            log.msg("Updating[2/2]: Creating %s in ConfigurationAPI" % (self))
            d = self._client._client.positions.create(
                **self._config
            )
            d.addErrback(self.failed, "update")
            return d

        d = self._client._client.positions.delete_one(
            self.name, **self._old_config
        )
        d.addCallbacks(create, self.failed, errbackArgs=['update'])
        return d


class APICalendar(APIRessource):
    def __init__(self, name, whitelabel, project, client, clientdb, old_id,
                 config={}, exists=True):
        super(APICalendar, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.calendars
        self.old_id = old_id
        self.clientdb = clientdb
        self.customer_id = old_id['customer_id']

    def __str__(self):
        return "Calendars `%s [parent_id: %s]@%s:%s`" % (
            self.name, self._config['parent_id'], self._whitelabel, self._project
        )

    def create(self, api_only=False):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        d = self._collection.create(
            name=self.name, **self._config
        )
        d.addErrback(self.failed, "create")
        if not api_only:
            d.addCallback(self.upgrade_scenario_object)
        else:
            log.msg('Skip scenario object migration for %s.' % (self,))
        return d

    def upgrade_scenario_object(self, value):
        d = self.clientdb.query_db(
            "select `id`, `scenario` "
            "from `adm_vocal_scenarios_obj` "
            "where `user`=%s "
            "and `type`='SPECIALDAYS' "
            "and `configuration` like '%%s:7:\"daypack\";s:%s:\"%s\"%%'" % (
                self.old_id['customer_id'],
                len(str(self.old_id['id'])),
                self.old_id['id'],
            )
        )

        def ask_id(result):
            def print_success(_, obj_id, scnr_id):
                log.msg(
                    'Updated SPECIALDAYS object in scenario [obj_id=%s/scnr_id=%s/calendar=%s]' % (
                        obj_id, scnr_id, self.name)
                )

            list_deferreds = []
            for row in result:
                d = self.clientdb.query_db(
                    "update `adm_vocal_scenarios_obj` "
                    "set `configuration` = replace(`configuration`, '\"daypack\";s:%s:\"%s\"', '\"daypack\";s:%s:\"%s\"') "
                    "where id=%s" % (
                        len(str(self.old_id['id'])),
                        self.old_id['id'],
                        len(str(value['id'])),
                        value['id'],
                        row[0]
                    )
                )
                d.addCallback(print_success, row[0], row[1])
                list_deferreds.append(d)

            return list_deferreds

        d.addCallback(ask_id)
        return d


class APISpecialDay(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        if config.get('end_date') == 'None':
            config.pop('end_date')
        super(APISpecialDay, self).__init__(name, project, whitelabel,
                                            client, config, exists)
        self._collection = self._client._client.specialdays

    def __str__(self):
        return "SpecialDay `(%s / %s)[calendar_id:%s, calendar_name:%s]@%s:%s`" % (
            self._config['start_date'], self._config.get('end_date'),
            self._config['calendar_id'], self._config['calendar_name'],
            self._whitelabel, self._project
        )

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._client._client.specialdays.create(
            **self._config
        ).addErrback(self.failed, "create")


class APIScenariosFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIScenariosFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.scenariosfolders

    def __str__(self):
        return "ScenariosFolder `%s@%s:%s`" % (
            self.name, self._whitelabel, self._project
        )


class APIScenario(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIScenario, self).__init__(name, project, whitelabel,
                                          client, config, exists)
        self._res_name = "Scenario"
        self._name = name
        self._collection = self._client._client.scenarios

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        return self._client._client.scenarios.create(
            **self._config
        ).addErrback(self.failed, "create")


class APIEntryPoint(APIRessource):
    def __init__(self, name, whitelabel, project, client, config={},
                 exists=True):
        super(APIEntryPoint, self).__init__(name, project, whitelabel,
                                            client, config, exists)
        if self.config('scenario') is None:
            self._config.pop('scenario')
        self._res_name = "EntryPoint"
        self._name = name
        self._collection = self._client._client.entrypoints


class APISoundFilesFolder(APIRessource):
    def __init__(self, name, whitelabel, project, client, old_id,
                 config={}, exists=True):
        super(APISoundFilesFolder, self).__init__(name, project, whitelabel, client, config,
                 exists)
        self._collection = self._client._client.soundfilesfolders
        self.old_id = old_id
        self.customer_id = old_id['customer_id']

    def __str__(self):
        return "SoundFilesFolder `%s [parent_id: %s]@%s:%s`" % (
            self.name, self._config['parent_id'], self._whitelabel, self._project
        )

    def create(self):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        d = self._collection.create(
            name=self.name, **self._config
        )
        d.addErrback(self.failed, "create")
        return d


class APISoundFile(APIRessource):
    def __init__(self, name, whitelabel, project, client, clientdb, old_id,
                 config={}, exists=True):
        super(APISoundFile, self).__init__(name, project, whitelabel,
                                           client, config, exists)
        self._collection = self._client._client.soundfiles
        self.old_id = old_id
        self.clientdb = clientdb

    def __str__(self):
        return "SoundFiles `(%s / %s / %s)[folderId:%s, folder name:%s]@%s:%s`" % (
            self._config['display_name'], self._config.get('path'),
            self._config['type'],
            self._config['folder_id'], self._config['folder_name'],
            self._whitelabel, self._project
        )

    @defer.inlineCallbacks
    def create(self, api_only=False):
        log.msg("Creating %s in ConfigurationAPI." % (self,))
        try:
            value = yield self._client._client.soundfiles.create(**self._config)

        except TrestConflict:
            log.msg("Data: %s" % self._config)
            folders = yield self._client._client.soundfilesfolders.read_all(
                whitelabel=self._config['whitelabel'], project=self._config['project']
            )
            _folder = {}
            for folder in folders:
                if folder['name'] == self._config['folder_name']:
                    _folder = folder
                    break

            value = {}
            if _folder:
                for soundfile in _folder['content']:
                    if soundfile['display_name'] == self._config['display_name']:
                        value = soundfile
                        break
            else:
                log.msg("ERROR[Missing folder] %s" % self._config)

        except Exception as e:
            log.msg("ERROR[%s]: Can't create soundfile : %s" % (str(e), str(self._config)))
            defer.returnValue(False)

        if not api_only and value:
            yield self.upgrade_file_scenario_object(value)
            yield self.upgrade_file_scenario_object_bis(value)
            yield self.upgrade_callroom_scenario_object_sound_field(value)
            yield self.upgrade_callroom_scenario_object_sound_field_bis(value)
            yield self.upgrade_callroom_scenario_object_onRinging_field(value)
            yield self.upgrade_callroom_scenario_object_onRinging_field_bis(value)
            yield self.upgrade_transfert_scenario_object(value)
            yield self.upgrade_transfert_scenario_object_bis(value)
            yield self.upgrade_dialog_scenario_object(value)
            yield self.upgrade_dialog_scenario_object_bis(value)
            yield self.upgrade_announcement_scenario_object(value)
            yield self.upgrade_announcement_scenario_object_bis(value)
            yield self.upgrade_queues_waiting_sound(value)
            yield self.upgrade_queues_waiting_sound_bis(value)
            yield self.upgrade_queues_holding_sound(value)
            yield self.upgrade_queues_holding_sound_bis(value)
            yield self.upgrade_agents_waiting_sound(value)
            yield self.upgrade_agents_waiting_sound_bis(value)
            yield self.upgrade_agents_holding_sound(value)
            yield self.upgrade_agents_holding_sound_bis(value)
            yield self.upgrade_supervisors_waiting_sound(value)
            yield self.upgrade_supervisors_waiting_sound_bis(value)
            yield self.upgrade_supervisors_holding_sound(value)
            yield self.upgrade_supervisors_holding_sound_bis(value)

        else:
            log.msg('Skip soundfile object migration for %s.' % (self,))
        defer.returnValue(value)

    def upgrade_file_scenario_object(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='FILE' "
                "and `configuration` like '%%s:5:\"sound\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated FILE object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound\";s:41:\"%s\"', '\"sound\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_file_scenario_object for %s" % self._config.get('path'))
            return value

    def upgrade_file_scenario_object_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='FILE' "
                "and `configuration` like '%%s:5:\"sound\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated FILE object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound\";s:40:\"%s\"', '\"sound\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_file_scenario_object_bis for %s" % self._config.get('path'))
            return value

    def upgrade_callroom_scenario_object_sound_field(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='CALLROOM' "
                "and `configuration` like '%%s:5:\"sound\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated CALLROOM object (sound field) in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound\";s:41:\"%s\"', '\"sound\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_callroom_scenario_object_sound_field for %s" % self._config.get('path'))
            return value

    def upgrade_callroom_scenario_object_sound_field_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='CALLROOM' "
                "and `configuration` like '%%s:5:\"sound\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated CALLROOM object (sound field) in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound\";s:40:\"%s\"', '\"sound\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_callroom_scenario_object_sound_field_bis for %s" % self._config.get('path'))
            return value

    def upgrade_callroom_scenario_object_onRinging_field(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='CALLROOM' "
                "and `configuration` like '%%s:9:\"onRinging\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated CALLROOM object (onRinging field) in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"onRinging\";s:41:\"%s\"', '\"onRinging\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_callroom_scenario_object_onRinging_field for %s" % self._config.get('path'))
            return value

    def upgrade_callroom_scenario_object_onRinging_field_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='CALLROOM' "
                "and `configuration` like '%%s:9:\"onRinging\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated CALLROOM object (onRinging field) in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"onRinging\";s:40:\"%s\"', '\"onRinging\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_callroom_scenario_object_onRinging_field_bis for %s" % self._config.get('path'))
            return value

    def upgrade_transfert_scenario_object(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='TRANSFERT' "
                "and `configuration` like '%%s:9:\"onRinging\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated TRANSFERT object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update adm_vocal_scenarios_obj "
                        "set configuration = replace(`configuration`, '\"onRinging\";s:41:\"%s\"', '\"onRinging\";s:%s:\"%s\"') "
                        "where id=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_transfert_scenario_object for %s" % self._config.get('path'))
            return value

    def upgrade_transfert_scenario_object_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='TRANSFERT' "
                "and `configuration` like '%%s:9:\"onRinging\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated TRANSFERT object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update adm_vocal_scenarios_obj "
                        "set configuration = replace(`configuration`, '\"onRinging\";s:40:\"%s\"', '\"onRinging\";s:%s:\"%s\"') "
                        "where id=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_transfert_scenario_object_bis for %s" % self._config.get('path'))
            return value

    def upgrade_dialog_scenario_object(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='DIALOG' "
                "and `configuration` like '%%s:10:\"sound_file\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated DIALOG object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:41:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_dialog_scenario_object for %s" % self._config.get('path'))
            return value

    def upgrade_dialog_scenario_object_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='DIALOG' "
                "and `configuration` like '%%s:10:\"sound_file\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated DIALOG object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:40:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_dialog_scenario_object_bis for %s" % self._config.get('path'))
            return value

    def upgrade_announcement_scenario_object(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='ANNOUNCEMENT' "
                "and `configuration` like '%%s:10:\"sound_file\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated DIALOG object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:41:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_announcement_scenario_object for %s" % self._config.get('path'))
            return value

    def upgrade_announcement_scenario_object_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `scenario` "
                "from `adm_vocal_scenarios_obj` "
                "where `user`=%s "
                "and `type`='ANNOUNCEMENT' "
                "and `configuration` like '%%s:10:\"sound_file\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, scnr_id):
                    log.msg(
                        'Updated DIALOG object in scenario [obj_id=%s/file_id=%s/file_path=%s]' % (
                            obj_id, scnr_id, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_scenarios_obj` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:40:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_announcement_scenario_object_bis for %s" % self._config.get('path'))
            return value

    def upgrade_queues_waiting_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_queues` "
                "where `user`=%s "
                "and `type`='queue' "
                "and `configuration` like '%%s:10:\"sound_file\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, queue_name):
                    log.msg(
                        'Updated QUEUE waiting sound (tts) [id=%s/queue_name=%s/file_path=%s]' % (
                            obj_id, queue_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_queues` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:40:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_queues_waiting_sound for %s" % self._config.get('path'))
            return value

    def upgrade_queues_waiting_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_queues` "
                "where `user`=%s "
                "and `type`='queue' "
                "and `configuration` like '%%s:10:\"sound_file\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, queue_name):
                    log.msg(
                        'Updated QUEUE waiting sound (upload) [id=%s/queue_name=%s/file_path=%s]' % (
                            obj_id, queue_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_queues` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:41:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_queues_waiting_sound_bis for %s" % self._config.get('path'))
            return value

    def upgrade_queues_holding_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_queues` "
                "where `user`=%s "
                "and `type`='queue' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, queue_name):
                    log.msg(
                        'Updated QUEUE holding sound (tts) [id=%s/queue_name=%s/file_path=%s]' % (
                            obj_id, queue_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_queues` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:40:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_queues_holding_sound for %s" % self._config.get('path'))
            return value

    def upgrade_queues_holding_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_queues` "
                "where `user`=%s "
                "and `type`='queue' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, queue_name):
                    log.msg(
                        'Updated QUEUE holding sound (upload) [id=%s/queue_name=%s/file_path=%s]' % (
                            obj_id, queue_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_queues` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:41:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_queues_holding_sound_bis for %s" % self._config.get('path'))
            return value

    def upgrade_agents_waiting_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_agents_users` "
                "where `user`=%s "
                "and `type`='agent' "
                "and `configuration` like '%%s:10:\"sound_file\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, agent_name):
                    log.msg(
                        'Updated AGENT waiting sound (tts) [id=%s/agent_name=%s/file_path=%s]' % (
                            obj_id, agent_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_agents_users` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:40:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_agents_waiting_sound for %s" % self._config.get('path'))
            return value

    def upgrade_agents_waiting_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_agents_users` "
                "where `user`=%s "
                "and `type`='agent' "
                "and `configuration` like '%%s:10:\"sound_file\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, agent_name):
                    log.msg(
                        'Updated AGENT waiting sound (upload) [id=%s/agent_name=%s/file_path=%s]' % (
                            obj_id, agent_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_agents_users` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:41:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_agents_waiting_sound_bis for %s" % self._config.get('path'))
            return value

    def upgrade_agents_holding_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_agents_users` "
                "where `user`=%s "
                "and `type`='agent' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, agent_name):
                    log.msg(
                        'Updated AGENT holding sound (tts) [id=%s/agent_name=%s/file_path=%s]' % (
                            obj_id, agent_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_agents_users` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:40:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_agents_holding_sound for %s" % self._config.get('path'))
            return value

    def upgrade_agents_holding_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_agents_users` "
                "where `user`=%s "
                "and `type`='agent' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, agent_name):
                    log.msg(
                        'Updated AGENT holding sound (upload) [id=%s/agent_name=%s/file_path=%s]' % (
                            obj_id, agent_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_agents_users` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:41:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_agents_holding_sound_bis for %s" % self._config.get('path'))
            return value

    def upgrade_supervisors_waiting_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_supervisors` "
                "where `user`=%s "
                "and `type`='supervisor' "
                "and `configuration` like '%%s:10:\"sound_file\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, supervisor_name):
                    log.msg(
                        'Updated SUPERVISOR waiting sound (tts) [id=%s/supervisor_name=%s/file_path=%s]' % (
                            obj_id, supervisor_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_supervisors` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:40:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_supervisors_waiting_sound for %s" % self._config.get('path'))
            return value

    def upgrade_supervisors_waiting_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_supervisors` "
                "where `user`=%s "
                "and `type`='supervisor' "
                "and `configuration` like '%%s:10:\"sound_file\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, supervisor_name):
                    log.msg(
                        'Updated SUPERVISOR waiting sound (upload) [id=%s/supervisor_name=%s/file_path=%s]' % (
                            obj_id, supervisor_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_supervisors` "
                        "set `configuration` = replace(`configuration`, '\"sound_file\";s:41:\"%s\"', '\"sound_file\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_supervisors_waiting_sound_bis for %s" % self._config.get('path'))
            return value

    def upgrade_supervisors_holding_sound(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_supervisors` "
                "where `user`=%s "
                "and `type`='supervisor' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:40:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, supervisor_name):
                    log.msg(
                        'Updated SUPERVISOR holding sound (tts) [id=%s/supervisor_name=%s/file_path=%s]' % (
                            obj_id, supervisor_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_supervisors` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:40:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_supervisors_holding_sound for %s" % self._config.get('path'))
            return value

    def upgrade_supervisors_holding_sound_bis(self, value):
        if value:
            d = self.clientdb.query_db(
                "select `id`, `nom` "
                "from `adm_vocal_supervisors` "
                "where `user`=%s "
                "and `type`='supervisor' "
                "and `configuration` like '%%s:18:\"sound_file_holding\";s:41:\"%s\"%%'" % (
                    self.old_id['customer_id'], self._config.get('path'),
                )
            )

            def ask_id(result):
                def print_success(_, obj_id, supervisor_name):
                    log.msg(
                        'Updated SUPERVISOR holding sound (upload) [id=%s/supervisor_name=%s/file_path=%s]' % (
                            obj_id, supervisor_name, self._config.get('path'))
                    )

                list_deferreds = []
                for row in result:
                    d = self.clientdb.query_db(
                        "update `adm_vocal_supervisors` "
                        "set `configuration` = replace(`configuration`, '\"sound_file_holding\";s:41:\"%s\"', '\"sound_file_holding\";s:%s:\"%s\"') "
                        "where `id`=%s" % (
                            self._config.get('path'),
                            len(str(value['id'])),
                            value['id'],
                            row[0]
                        )
                    )
                    d.addCallback(print_success, row[0], row[1])
                    list_deferreds.append(d)

                return value

            d.addCallback(ask_id)
            return d
        else:
            log.msg("SyncError: can't upgrade upgrade_supervisors_holding_sound_bis for %s" % self._config.get('path'))
            return value
