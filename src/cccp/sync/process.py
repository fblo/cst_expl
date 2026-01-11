#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.clients.head import head
from cccp.sync.requester import HeadRequester
from cccp.protocols.utils import print_object
from cccp.protocols.errors import ProcessViewerError
import cccp.protocols.messages.base as message

# CPI stands for Consistent Process Info which is informations about active processes given by heads.
CPI_STATE_INACTIVE = "inactive"
CPI_STATE_ACTIVE = "active"
CPI_STATE_ERROR = "error"
CPI_PROJECT_PREFIX = "Head_"


# project/process_type/server
# server/project/process_type
#
# Process : active process, it's different from ConfProcess
#
class Process:
    name = ""
    debug_level = 0
    pid = 0
    port = 0
    path = ""
    project_name = ""
    state = CPI_STATE_INACTIVE
    version = ""
    config_path = ""
    edition = ""
    start_date = ""
    ip = ""
    process_class = ""
    process_id = ""
    local_id = 0
    description = ""

    def __init__(self, path, father):
        self.path = path
        self.requester = father.requester
        self.refresh()

    def refresh(self):
        try:
            header = self.requester.get_header(self.path)
        except:
            raise ProcessViewerError(self.path)
        self.description = header.name
        objects = self.requester.get_objects(self.path)
        self.name = objects.instance
        self.debug_level = objects.debug_level
        self.pid = objects.pid
        self.port = objects.port
        self.project_name = objects.project
        self.state = objects.state
        self.version = objects.version
        self.edition = objects.edition
        self.ip = objects.address
        if objects.path is not None:
            self.config_path = objects.path[11:]
        self.start_date = objects.start_date
        self.process_id = objects.process_id
        self.process_class = objects.process_class
        self.local_id = objects.local_id
        return self

    def __repr__(self):
        return print_object(self)
        # return str(vars(self))


class HeadProcess(Process):
    pass


class ProjectProcess(HeadProcess):
    @property
    def dispatch(self):
        return self.get_process("ccenter_dispatch")

    @property
    def store(self):
        return self.get_process("consistent_store")

    @property
    def ccxml(self):
        return self.get_process("ccenter_ccxml")

    @property
    def voip(self):
        return self.get_process("ccenter_voip")

    @property
    def logger(self):
        return self.get_process("consistent_logger")

    @property
    def proxy(self):
        return self.get_process("ccenter_proxy")

    @property
    def queues(self):
        return self.get_process("ccenter_queues")

    def get_process(self, name):
        for process in self.processes:
            if name == process.process_class:
                return process
        raise ProcessViewerError(message.PROCESS_NOT_FOUND % name)

    def get_processes(self):
        children = self.requester.get_children(self.path)
        processes = []
        for e in children:
            processes.append(Process(self.path + "/" + e.name, self))
        return processes

    processes = property(get_processes)


class ServerProcess(HeadProcess):
    def __init__(self, path="", ip="localhost", port=20000):
        self.requester = HeadRequester(ip, port)
        self.requester.socket.objects_with_all_fields = True
        if path == "":
            path = "/proc/" + self.requester.get_children("/proc/localhost")[0].name
        Process.__init__(self, path, self)
        return

    def project(self, name):
        children = self.requester.get_children(self.path)
        for e in children:
            if e.name == CPI_PROJECT_PREFIX + name:
                return ProjectProcess(self.path + "/" + e.name, self)
        raise ProcessViewerError(message.PROJECTPROCESS_NOT_FOUND % name)

    def get_projects(self):
        children = self.requester.get_children(self.path)
        projects = []
        for e in children:
            if e.name[:5] == CPI_PROJECT_PREFIX:
                projects.append(ProjectProcess(self.path + "/" + e.name, self))
        return projects

    projects = property(get_projects)


#
# Because you have to connect to the good head to
# ask about its sons processes, each ServerProcess
# object opens a connection to the corresponding head.
# So connection to head and ServerProcess object are tied.
# And that's why ProcessViewer, which is first a connection,
# inherit from ServerProcess.
#
# This implies that there's not more ServerProcess created than needed.
# An improvment to this will be a class dictionary field which store the
# requester for each server path.
#
class ProcessViewer(ServerProcess):
    def servers_paths(self, path="/proc"):
        l = []
        path_children = self.requester.get_children(path)
        for e in path_children:
            if e.name == "Head_Main":
                l.append((path[6:], e.expression[:-6], int(e.expression[-5:])))
            else:
                l += self.servers_paths(path + "/" + e.name)
        return l

    #
    # First obtain the list of connections to Head to query processes informations.
    # ServerProcess will open head_server connections to query more informations.
    #
    def get_servers(self):
        servers = []
        for server_path, server_ip, server_port in self.servers_paths():
            servers.append(
                ServerProcess(
                    "/proc/" + server_path + "/Head_Main", server_ip, server_port
                )
            )
        return servers

    servers = property(get_servers)

    def server_connection_info(self, name):
        children = self.requester.get_children("/proc/" + name)
        ip = ""
        port = 0
        for e in children:
            if e.name == "Head_Main":
                ip = e.expression[:-6]
                port = int(e.expression[-5:])
                break
        if ip == "":
            raise ProcessViewerError(message.SERVERPROCESS_NOT_FOUND % name)
        return (ip, port)

    def server(self, name):
        (ip, port) = self.server_connection_info(name)
        return ServerProcess("/proc/" + name + "/Head_Main", ip, port)


class ProcessPilot(head):
    def __init__(self, process):
        self.process = process
        head.__init__(self, process.requester.ip, 20000)

    def set_debug_level(self, debug_level):
        self.set_process_debug_level(self.process.process_id, debug_level)
        self.step()

    def process_debug_level_set(self, process_id):
        self.step_done()

    def connection_ok(
        self,
        server_version,
        explorer_login,
        explorer_password,
        head_path,
        main_head_port,
    ):
        self.step_done()
