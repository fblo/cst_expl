#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>

from cccp.protocols.clients.explorer import explorer
from cccp.protocols.errors import HeadRequesterError
import cccp.protocols.messages.base as message
import logging as log

CCC_DEFAULT_HEAD_PORT = 20000
EXPLORER_SESSION_ID = 1
EXPLORER_SYSTEM_ID = 1
EXPLORER_FORMAT_ID = 1
EXPLORER_LIST_ID = 1


# ExplorerRequester is here to initiate a connexion with an Explorer Server like Head or Dispatch.
#
class ExplorerRequester(explorer):
    def __init__(self, ip, port, login="admin", password="admin"):
        self.ip = ip
        self.port = port
        explorer.__init__(self, self.ip, self.port)
        self.login(EXPLORER_SESSION_ID, login, password, 0, False)
        self.step()
        (result, reason) = self.step_result
        if not result:
            raise ExplorerRequesterError(message.LOGIN_FAILED % reason)
        self.use_default_namespaces_index()
        self.step()

    def use_default_namespaces_index_ok(self):
        log.debug("Use default namespaces index ok")
        self.step_done()

    def connection_ok(self, server_version, server_date):
        log.debug("Connexion ok : %s, %s" % (server_version, server_date))
        self.step_done()

    def login_failed(self, session_id, reason):
        log.exception(
            "ExplorerRequester login failed on %s:%d session_id:%d, reason:%s"
            % (self.ip, self.port, session_id, reason)
        )
        self.step_done((False, reason))

    def login_ok(self, session_id, user_id, explorer_id):
        log.debug("Login ok : %d, %s, %s" % (session_id, user_id, explorer_id))
        self.step_done((True, ""))

    def result(self, session_id, system_id, result):
        log.debug("Result : %d, %d, %d" % (session_id, system_id, result))
        self.step_done(result)


#
# HeadRequester deal with Head objects : the nodes.
#
class HeadRequester(ExplorerRequester):
    def __init__(self, ip="localhost", port=CCC_DEFAULT_HEAD_PORT):
        ExplorerRequester.__init__(self, ip, port)

    def get_children(self, path):
        self.query_node_children(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path)
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)

        (result, object) = self.step()
        if result != 0:
            raise HeadRequesterError(message.NONE_RESULT)
        return object.nodes

    def search_paths(self, begin, end):
        result = []
        for node in self.get_children(begin):
            if node.name == end:
                return begin + "/" + node.name
            result.append(self.search_paths(begin + "/" + node.name, end))
        return result

    def get_header(self, path):
        self.query_node_header(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path)
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)
        (result, header) = self.step()
        if result != 0:
            raise HeadRequesterError(message.NONE_RESULT)
        return header

    def get_objects(self, path):
        self.query_node_object_content(
            EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path, False, False, ""
        )
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)
        (result, objects) = self.step()
        if result != 0:
            raise HeadRequesterError(message.NONE_RESULT)
        return objects

    def put_content(self, path, objects):
        self.update_node_object(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path, objects)
        result = self.step()
        if result != 0:
            raise HeadRequesterError(message.RESULT % result, result)
        return result

    def get_content(self, path):
        self.query_node_object_content(
            EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path, False, True, ""
        )
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)
        (result, content) = self.step()
        if result != 0:
            raise HeadRequesterError(message.RESULT % result)
        return content

    def create_node(self, path):
        self._create_node(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path)
        return self.step()

    def delete_node(self, path):
        self._delete_node(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path)
        return self.step()

    def move_node(self, path, new_path):
        self._move_node(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID, path, new_path)
        return self.step()

    def node_children_response(self, session_id, system_id, object, result):
        log.debug("children_response : Object received")
        self.step_done((result, object))

    def node_header_response(self, session_id, system_id, object, result):
        log.debug("header_response : Header received")
        self.step_done((result, object))

    def node_object_content_response(self, session_id, system_id, object, result):
        log.debug("object_content_response : Object received")
        self.step_done((result, object))

    def node_raw_object_content_response(
        self, session_id, system_id, object, uncompressed_size, result
    ):
        log.debug("raw_object_content_response : Object received")
        self.step_done((result, object))


class DispatchRequester(ExplorerRequester):
    def __init__(self, ip, port):
        self.next_format_id = 1
        ExplorerRequester.__init__(self, ip, port)

    def get_list(self, name, filter="", object_id=0):
        self.query_list(
            EXPLORER_SESSION_ID,
            EXPLORER_SYSTEM_ID,
            "/dispatch",
            object_id,
            name,
            filter,
            0,
            "",
            0,
        )
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)
        consistent_list = self.step()

        l = []
        for item in consistent_list.items:
            l.append(item.item_id)
        return l

    def set_format(self, format):
        format.format_id = self.next_format_id
        self.set_object_format(EXPLORER_SESSION_ID, format)
        self.next_format_id += 1
        return format.format_id

    def get_object(self, id, format_id):
        self.query_object(
            EXPLORER_SESSION_ID,
            EXPLORER_SYSTEM_ID,
            "/dispatch",
            id,
            format_id,
            EXPLORER_LIST_ID,
        )
        self.stop_query(EXPLORER_SESSION_ID, EXPLORER_SYSTEM_ID)
        return self.step()

    def list_response(self, session_id, system_id, object):
        log.debug("list_reponse : Object received")
        self.step_done(object)

    def object_response(self, session_id, system_id, object, list_id):
        log.debug("object_reponse : Object received")
        self.step_done(object)
