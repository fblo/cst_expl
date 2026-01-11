import datetime
from cccp.async.dispatch import DispatchClient
from twisted.internet import reactor, defer

# fixture
fixture = [
    ('setup_queue', {
        'working_sessions_count': 0, 'waiting_tasks_count': 0,
        'logged_sessions_count': 0, 'latent_sessions_count': 0,
        "contact_duration.count('0')": 8.41478490829468,
        'oldest_waiting_date': None,
        "waiting_duration.max('0')": 10.2719340324402,
        "not_manageable_with_latent_users.count('0')": 0,
        'display_name': 'Support Vocal1', 'running_tasks_count': 0,
        "managed_tasks.count('0')": 1, 'outbound_sessions_count': 0,
        "contact_duration.max('0')": 8.41478490829468,
        'oldest_contact_date': None,
        "waiting_duration.count('0')": 10.2719340324402,
        'withdrawn_sessions_count': 0, 'supervision_sessions_count': 0,
        "failed_tasks.count('0')": 0, 'name': 'Q_133_ref__Support_vocal',
        "max_estimated_waiting_time_threshold.count('0')": 0,
        "max_waiting_time_threshold.count('0')": 0,
        "not_manageable_without_latent_users.count('0')": 0}),
    ('session', {
        'terminate_date': None, 'last_record.value': '', 'session_type': 1,
        'session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'create_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 916541),
        'record_active.value': ''}),
    ('queue', {
        'attributes.remote_number.value': 'sip:430821687@connectics.fr',
        'queue_name': 'Q_133_ref__Support_vocal',
        'attributes.local_number.value': 'sip:0170986339@connectics.fr',
        'session.session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301'}), # NOQA
    ('task', {
        'manager_session.profile_name': '', 'stop_waiting_date': None,
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': None, 'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'queue_type': 'queue', 'management_date': None,
        'queue_display_name': 'Support Vocal1', 'post_management_date': None,
        'manager_session.user.login': '',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('task', {
        'manager_session.profile_name': '',
        'stop_waiting_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': None, 'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'queue_type': 'queue', 'management_date': None,
        'queue_display_name': 'Support Vocal1', 'post_management_date': None,
        'manager_session.user.login': '',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('task', {
        'manager_session.profile_name': '',
        'stop_waiting_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': None, 'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'queue_type': 'queue',
        'management_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'queue_display_name': 'Support Vocal1', 'post_management_date': None,
        'manager_session.user.login': '',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('task', {
        'manager_session.profile_name': 'Profile Support',
        'stop_waiting_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': None, 'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA 'queue_type': 'queue',
        'management_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'queue_display_name': 'Support Vocal1', 'post_management_date': None,
        'manager_session.user.login': 'gric',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('task', {
        'manager_session.profile_name': 'Profile Support',
        'stop_waiting_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': None, 'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA  'queue_type': 'queue',
        'management_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'queue_display_name': 'Support Vocal1',
        'post_management_date': datetime.datetime(2017, 5, 24, 7, 45, 44, 661931), # NOQA
        'manager_session.user.login': 'gric',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('task', {
        'manager_session.profile_name': 'Profile Support',
        'stop_waiting_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'task_id': 'task_1188@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301',
        'end_date': datetime.datetime(2017, 5, 24, 7, 46, 14, 665596),
        'parent_call_session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'queue_type': 'queue',
        'management_date': datetime.datetime(2017, 5, 24, 7, 45, 36, 247153),
        'queue_display_name': 'Support Vocal1',
        'post_management_date': datetime.datetime(2017, 5, 24, 7, 45, 44, 661931), # NOQA
        'manager_session.user.login': 'gric',
        'start_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 973649)}),
    ('session', {
        'terminate_date': datetime.datetime(2017, 5, 24, 7, 46, 14, 666815),
        'last_record.value': '', 'session_type': 1,
        'session_id': 'session_1184@12040.1495110344.Ccxml.vs-dev-prd-cst-fr-301', # NOQA
        'create_date': datetime.datetime(2017, 5, 24, 7, 45, 25, 916541),
        'record_active.value': ''}),

]


@defer.inlineCallbacks
def process_fixture():
    i = 0

    def printer(self, target, data):
        if 'task_end_date' in data[0] and not data[0]['task_end_date']['value']: # NOQA
            print 'element_set'

        if 'task_end_date' in data[0] and data[0]['task_end_date']['value'] \
                not in ["", "stop"] and "task_start_date" not in data:
            print "element_unset"
        print data, "\n"

    dclient = DispatchClient("nom", "ip", "port")
    dclient.subscriber.send = printer
    result = dclient.subscribe_communication(
        'roman',
        [
            'channel', 'waiting_duration', 'managing_duration',
            'task_start_date', 'total_duration', 'task_end_date',
            'initial_agent_name', 'current_agent_name', 'call_profile',
            'initial_queue_name', 'current_queue_name', 'from', 'to',
            'managing_duration', 'total_duration',
            'communication_create_date',
            'comunication_session_id', 'communication_task_id'
        ],
        ["Profile Support"],
        ["Support Vocal1"]
    )

    print "Init subscription: ", result["id"], "\n"
    for query in fixture:
        if query[0] == "setup_queue":
            yield dclient.on_service_update(query[1])

        if query[0] == "session":
            reactor.callLater(i, dclient.on_communication_session_update, query[1]) # NOQA

        if query[0] == "queue":
            reactor.callLater(i, dclient.on_communication_queue_update, query[1]) # NOQA

        if query[0] == "task":
            reactor.callLater(i, dclient.on_communication_task_update, query[1]) # NOQA

        i += 0.15
    reactor.callLater(5, reactor.stop)

reactor.callWhenRunning(process_fixture)
reactor.run()
