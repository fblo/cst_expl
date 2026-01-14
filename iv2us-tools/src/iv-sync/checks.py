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

from ivsync.utils import handle_error
from twisted.internet import defer
from twisted.python import log

VERIFY_RANGE = {
    'transfer_targets_folders': 5,
    'transfer_targets': 25,
    'projects': 1,
    'whitelabels': 1,
    'queues_folders': 5,
    'vocal_queues': 25,
    'mail_queues': 25,
    'profiles_folders': 25,
    'profiles': 25,
    'agents': 25,
    'supervisors': 25,
    'positions_folders': 5,
    'positions': 25,
    'agents_folders': 5,
    'supervisors_folders': 5,
    'calendars': 5,
    'specialdays': 25,
    'scenarios_folders': 5,
    'scenarios': 25,
    'entrypoints': 25,
    'soundfilesfolders': 5,
    'soundfiles': 1,
}

verify_map = {
    'agents': ('get_agent',),
    'supervisors': ('get_supervisor',),
    'transfer_targets_folders': ('get_transfer_targets_folder',),
    'transfer_targets': ('get_transfer_target',),
    'queues_folders': ('get_queues_folder',),
    'vocal_queues': ('get_vocal_queue',),
    'mail_queues': ('get_mail_queue',),
    'profiles_folders': ('get_profiles_folder',),
    'profiles': ('get_profile',),
    'positions_folders': ('get_positions_folder',),
    'positions': ('get_position',),
    'agents_folders': ('get_agents_folder',),
    'supervisors_folders': ('get_supervisors_folder',),
    'calendars': ('get_calendar',),
    'specialdays': ('get_specialday',),
    'scenarios_folders': ('get_scenarios_folder',),
    'scenarios': ('get_scenario',),
    'entrypoints': ('get_entrypoint',),
    'soundfilesfolders': ('get_soundfiles_folder',),
    'soundfiles': ('get_soundfile',),
}


@defer.inlineCallbacks
def verify_ressources(ressources, ressource_type, transaction,
                      configapi_client, args):
    res_deferreds = []
    results = []

    for different_folder in ressources:
        limit = len(different_folder)
        offset = 0
        while offset <= limit:
            for res in different_folder[
                    offset:offset + VERIFY_RANGE[ressource_type]]:
                log.msg("Found %s in Portal DB." % res)
                d = getattr(configapi_client, verify_map[ressource_type][0])(res)

                def verify_exists(res, transaction):
                    if res.exists():
                        log.msg("Found %s in ConfigurationAPI." % (res,))
                    else:
                        transaction.create_ressource(res, ressource_type)

                    return res
                d.addCallbacks(verify_exists, handle_error, (transaction,))
                d.addCallback(res.compare, transaction)
                res_deferreds.append(d)

            offset += VERIFY_RANGE[ressource_type]
            results += yield defer.gatherResults(res_deferreds)
            res_deferreds = []

    defer.returnValue(results)


@defer.inlineCallbacks
def verify_projects(projects, configapi_client, transaction, args):
    configuration_deferreds = []
    results = []

    limit = len(projects)
    offset = 0

    while offset <= limit:
        for project in projects[offset:offset + VERIFY_RANGE['projects']]:
            log.msg("Found %s in Portal DB." % (project,))
            d = configapi_client.get_project(project)

            def verify_exists(project, transaction):
                if project.exists():
                    log.msg("Found %s in ConfigurationAPI." % (project,))

                else:
                    transaction.create_project(project)

            d.addCallbacks(verify_exists, handle_error, (transaction,))
            configuration_deferreds.append(
                verify_project_configuration(
                    project, transaction,
                    configapi_client, args)
            )

        offset += VERIFY_RANGE['projects']

        results += yield defer.gatherResults(configuration_deferreds)
        configuration_deferreds = []

    defer.returnValue(results)


@defer.inlineCallbacks
def verify_whitelabels(whitelabels, configapi_client, transaction, args):
    whitelabel_deferreds = []
    results = []

    limit = len(whitelabels)
    offset = 0

    while offset <= limit:
        for whitelabel in whitelabels[
                offset:offset + VERIFY_RANGE['whitelabels']]:
            log.msg("Found %s in Portal DB." % (whitelabel,))
            d = configapi_client.get_whitelabel(whitelabel)

            def verify_exists(whitelabel, transaction):
                if whitelabel.exists():
                    log.msg("Found %s in ConfigurationAPI." % (whitelabel,))

                else:
                    transaction.create_whitelabel(whitelabel)

                return whitelabel

            d.addCallbacks(verify_exists, handle_error, (transaction,))

            d = whitelabel.get_projects(args.project)
            d.addCallbacks(
                verify_projects, handle_error,
                (configapi_client, transaction, args))
            whitelabel_deferreds.append(d)

        offset += VERIFY_RANGE['whitelabels']

        results += yield defer.gatherResults(whitelabel_deferreds)
        whitelabel_deferreds = []

    defer.returnValue(results)


def verify_project_configuration(project, transaction, configapi_client, args):
    if args.calendarsapi:
        calendars_deferred = project.get_calendars()
        calendars_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('calendars', transaction, configapi_client, args))

        return defer.gatherResults([calendars_deferred])

    if args.specialdaysapi:
        specialdays_deferred = project.get_specialdays()
        specialdays_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('specialdays', transaction, configapi_client, args))

        return defer.gatherResults([specialdays_deferred])

    if args.soundfilesfoldersapi:
        soundfilesfolders_deferred = project.get_soundfiles_folders()
        soundfilesfolders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('soundfilesfolders', transaction, configapi_client, args))

        return defer.gatherResults([soundfilesfolders_deferred])

    if args.soundfilesapi:
        soundfiles_deferred = project.get_soundfiles()
        soundfiles_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('soundfiles', transaction, configapi_client, args))

        return defer.gatherResults([soundfiles_deferred])

    else:
        sync_vq, sync_mq = defer.Deferred(), defer.Deferred()
        queues_folders_deferred = project.get_queues_folders(sync_vq, sync_mq)
        queues_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('queues_folders', transaction, configapi_client, args))

        vocal_queues_deferred = project.get_vocal_queues(sync_vq)
        vocal_queues_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('vocal_queues', transaction, configapi_client, args))

        mail_queues_deferred = project.get_mail_queues(sync_mq)
        mail_queues_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('mail_queues', transaction, configapi_client, args))

        psync = defer.Deferred()
        profiles_folders_deferred = project.get_profiles_folders(psync)
        profiles_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('profiles_folders', transaction, configapi_client, args))

        profiles_deferred = project.get_profiles(psync)
        profiles_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('profiles', transaction, configapi_client, args))

        usync = defer.Deferred()
        agents_folders_deferred = project.get_agents_folders(usync)
        agents_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('agents_folders', transaction, configapi_client, args))

        agents_deferred = project.get_agents(usync)
        agents_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('agents', transaction, configapi_client, args))

        usync = defer.Deferred()
        supervisors_folders_deferred = project.get_supervisors_folders(usync)
        supervisors_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('supervisors_folders', transaction, configapi_client, args))

        supervisors_deferred = project.get_supervisors(usync)
        supervisors_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('supervisors', transaction, configapi_client, args))

        psync = defer.Deferred()
        positions_folders_deferred = project.get_positions_folders(psync)
        positions_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('positions_folders', transaction, configapi_client, args))

        positions_deferred = project.get_positions(psync)
        positions_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('positions', transaction, configapi_client, args))

        tsync = defer.Deferred()
        transfer_targets_folders_deferred = project.get_transfer_targets_folders(tsync)
        transfer_targets_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('transfer_targets_folders', transaction, configapi_client, args))

        transfer_targets_deferred = project.get_transfer_targets(tsync)
        transfer_targets_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('transfer_targets', transaction, configapi_client, args))

        ssync = defer.Deferred()
        scenarios_folders_deferred = project.get_scenarios_folders(ssync)
        scenarios_folders_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('scenarios_folders', transaction, configapi_client, args))

        scenarios_deferred = project.get_scenarios(ssync)
        scenarios_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('scenarios', transaction, configapi_client, args))

        entrypoints_deferred = project.get_entrypoints(ssync)
        entrypoints_deferred.addCallbacks(
            verify_ressources, handle_error,
            ('entrypoints', transaction, configapi_client, args))

        return defer.gatherResults(
            [
                queues_folders_deferred,
                vocal_queues_deferred,
                mail_queues_deferred,
                profiles_folders_deferred,
                profiles_deferred,
                agents_folders_deferred,
                supervisors_folders_deferred,
                agents_deferred,
                supervisors_deferred,
                positions_folders_deferred,
                positions_deferred,
                transfer_targets_folders_deferred,
                transfer_targets_deferred,
                scenarios_folders_deferred,
                scenarios_deferred,
                entrypoints_deferred
            ]
        )
