#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>

from cccp.protocols.converter import Converter
from cccp.protocols.classes import all_classes_by_name, CLASS_FIELDS_BY_NAME, FIELD_TYPE
from cccp.protocols.errors import ConfigDBError, HeadRequesterError
from cccp.sync.requester import HeadRequester, DispatchRequester
from cccp.sync.process import ProcessViewer
from cccp.usage.request import UsageDBRequest

import cccp.protocols.messages.base as message


class ConfigDB:
    def __init__(self, host=None):
        if host is None:
            self.requester = HeadRequester()
        else:
            self.requester = HeadRequester(host)

    def list(self, path):
        result = []
        try:
            nodes = self.requester.get_children(path)
            for node in nodes:
                result.append(node.name)
            return result
        except HeadRequesterError:
            raise ConfigDBError(message.PATH_NOT_FOUND % path)
            return result

    def create(self, path):
        result = self.requester.create_node(path)

    def delete(self, path, force=False):
        if force or self.is_empty(path):
            result = self.requester.delete_node(path)
        else:
            raise ConfigDBError(message.DIRECTORY_NOT_EMPTY % path)

    def is_empty(self, path):
        """
        .. todo::
            Update variable naming convention
        """
        l = self.list(path)

        if len(l) == 0:
            return True
        else:
            return False

    def exists(self, path):
        try:
            result = self.requester.get_header(path)
        except HeadRequesterError:
            return False
        else:
            return True

    def move(self, source, destination):
        result = self.requester.move_node(source, destination)

    def copy(self, source, destination):
        self.create(destination)
        self.put(destination, self.get(source))

    def get(self, path, builtin_mode=False):
        try:
            objects = self.requester.get_content(path)

        except HeadRequesterError:
            raise ConfigDBError(message.PATH_NOT_FOUND % path)

        if builtin_mode:
            return objects_to_builtins(o, type(o))
        else:
            return objects

    def put(self, path, objects):
        if "tree" in dir(objects):
            objects = objects.tree
        try:
            result = self.requester.put_content(path, objects)
        except HeadRequesterError as e:
            if e.result == 1:
                raise ConfigDBError(message.PATH_NOT_FOUND % path)
            else:
                raise e


class UsageDB:
    def __init__(self, project, server="", host="localhost", port=0):
        if port == 0:
            if server == "":
                port = ProcessViewer(ip=host).project(project).dispatch.port
            else:
                port = (
                    ProcessViewer(ip=host).server(server).project(project).dispatch.port
                )
        self.string_result = False
        self.requester = DispatchRequester(host, port)

    def ls(self, field_name=""):
        return self.search(field_name)

    def search(self, field_name, class_name="ccenter_dispatch_db"):
        """
        .. todo::
            Update variable naming convention
        """
        if field_name == "":
            return all_classes_by_name[class_name][CLASS_FIELDS_BY_NAME].keys()

        f = field_name.split(".", 1)
        current_field = f[0]

        if len(f) > 1:
            next_field = f[1]
        else:
            next_field = ""

        field_type = all_classes_by_name[class_name][CLASS_FIELDS_BY_NAME][
            current_field
        ][FIELD_TYPE]

        if type(field_type) == tuple:
            field_class_name = field_type[1]
            return self.search(next_field, field_class_name)

    def query(self, dict_request, class_name="ccenter_dispatch_db", object_id=0):
        """
        .. todo::
            Update variable naming convention
        """
        request = UsageDBRequest(dict_request, class_name)
        d = {}

        for name, content_type in request.t_list_fields:
            l = []
            objects_ids = self.requester.get_list(name, request.filter(name), object_id)
            format_id = self.requester.set_format(request.format(name))

            for object_id in objects_ids:
                o = self.requester.get_object(object_id, format_id)
                e = {}

                for v in o.values:
                    if self.string_result:
                        e[request.field_name[v.field_index]] = str(v.value)
                    else:
                        e[request.field_name[v.field_index]] = v.value

                self.query(request.dict_request[name], content_type, object_id)
                l.append(e)

            d[name] = l

        return d

    def raw_query(self, db_root, format_fields, filter):
        """
        .. todo::
            Update variable naming convention
        """
        objects_ids = self.requester.get_list(db_root, filter)
        format_id = self.requester.set_format(
            Converter().create_cst_object(format_fields)[0]
        )
        t = []
        for object_id in objects_ids:
            o = self.requester.get_object(object_id, format_id)
            l = ["" for i in range(len(format_fields))]
            for e in o.values:
                if hasattr(e, "value"):
                    l[e.field_index] = e.value
            t.append(l)
        return t
