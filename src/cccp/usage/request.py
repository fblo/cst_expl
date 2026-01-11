#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>
from cccp.usage.criterion import criterion_parser

from cccp.protocols.ccc_types import *
from cccp.protocols.classes import *
from cccp.protocols.errors import UsageDBError
import cccp.protocols.messages.base as message


class UsageDBRequest:
    def __init__(self, dict_request, class_name):
        self.dict_request = dict_request
        self.class_name = class_name
        self.class_fields = all_classes_by_name[class_name][CLASS_FIELDS_BY_NAME]
        self.field_name = {}

    def get_t_list_fields(self):
        l = []
        for name in self.dict_request:
            if name in self.class_fields:
                field_type = self.class_fields[name][FIELD_TYPE]
                if type(field_type) is tuple:
                    (field_type, content_type) = field_type
                    if field_type == t_list:
                        l.append((name, content_type))
            else:
                raise UsageDBError(message.UNKNOWN_FIELD % name)
        return l

    t_list_fields = property(
        get_t_list_fields,
    )

    def format(self, t_list_name):
        o = consistent_protocol_object_format()
        i = 1
        content_class_name = self.class_fields[t_list_name][FIELD_TYPE][FIELD_TYPE]
        class_fields = all_classes_by_name[content_class_name][CLASS_FIELDS_BY_NAME]
        for name in self.dict_request[t_list_name]:
            field_type = class_fields[name][FIELD_TYPE]
            if type(field_type) is not tuple:
                f = consistent_protocol_object_format_field()
                f.field_index = i
                f.name = name
                o.fields.append(f)
                self.field_name[i] = name
                i += 1
        return o

    def filter_criterion(self, name, criterion):
        if criterion == "":
            return ""
        d = criterion_parser.parseString(str(criterion))
        if d is None:
            return ""
        s = d[0]
        n = s.count("%s")
        if n == 2:
            s = s % name, name
        else:
            s = s % name
        return s

    def filter(self, t_list_name):
        filter = ""
        content_class_name = self.class_fields[t_list_name][FIELD_TYPE][FIELD_TYPE]
        class_fields = all_classes_by_name[content_class_name][CLASS_FIELDS_BY_NAME]
        for name in self.dict_request[t_list_name]:
            if name in class_fields:
                field_type = class_fields[name][FIELD_TYPE]
                if type(field_type) is not tuple:
                    criterion = self.filter_criterion(
                        name, self.dict_request[t_list_name][name]
                    )
                    if criterion != "":
                        filter += criterion + " and "
        if filter != "":
            filter = ".[ " + filter[0 : len(filter) - 5] + " ]"
        return filter
