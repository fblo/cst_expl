#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>
#    - GRIC <gric@interact-iv.com>

from cccp.protocols.utils import new_object


class Converter(object):

    def __init__(self):
        self._field_index = -1
        self.query_table = {}

    def create_cst_object(self, xqueries_list):
        _list = []
        for row in sorted(xqueries_list):
            __list = _list
            s_row = row.split(".")

            for element in s_row:
                length = len(__list)
                if not [item for item in __list if item[0] == element]:
                    __list.append((element, []))
                    length = len(__list)

                __list = __list[length - 1][1]

        self._field_index = -1
        self.query_table = {}
        obj = new_object("consistent_protocol_object_format")
        obj.format_id = 1
        obj.fields = self._extract_fields(_list)
        return (obj, dict(self.query_table))

    def _extract_fields(self, _field_list, _name=""):
        fields = []

        for name, _list in _field_list:
            obj = new_object("consistent_protocol_object_format_field")
            obj.field_index = self._next_field_index()

            if "(" in name:
                obj.query = name[name.index("(") + 2: -2]
                obj.name = name[:name.index("(")]

            else:
                obj.name = name

            obj.fields = self._extract_fields(
                _list,
                _name=_name + '.' + name if _name else name
            )
            if not _list:
                self.query_table[
                    self._field_index
                ] = _name + '.' + name if _name else name

            fields.append(obj)

        return fields

    def _next_field_index(self):
        self._field_index += 1
        return self._field_index
