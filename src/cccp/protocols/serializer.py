#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

import datetime
from time import mktime

from cccp.protocols import classes, methods

from cccp.protocols.ccc_types import *
from cccp.protocols.errors import SerializerError, SerializerMethodError, ConfigDBError
from cccp.protocols.utils import new_object

import cccp.protocols.messages as message

SERIALIZATION_COMPLETE = 0


class Serializer(object):
    ids = set()
    max_new_id = 0

    def __init__(self, pathes_sent=False):
        self.pathes_sent = pathes_sent

    def get_object_fullname(self, objects):
        if type(objects) is dict:
            namespace = classes.find_namespace_from_dict(objects)
            if namespace == "":
                raise SerializerError(
                    message.NAMESPACE_NOT_FIND_FROM_DICT % str(objects)
                )
            objects = builtins_to_objects(objects, namespace)
        class_id, fields, namespace = classes.all_classes_by_name[
            objects.__class__.__name__
        ]
        return namespace + "." + objects.__class__.__name__

    def serialize_pathes(self):
        if not self.pathes_sent:
            for path in classes.all_namespaces_by_id.values():
                self.serialize_string(path)
            self.pathes_sent = True

    def serialize_cdep_objects(self, objects):
        self.init_ids(objects)
        if type(objects) is dict:
            namespace = find_namespace_from_dict(objects)
            if namespace == "":
                raise ConfigDBError(message.NAMESPACE_NOT_FIND_FROM_DICT % str(objects))
            objects = builtins_to_objects(objects, namespace)
        self.data = []
        self.serialize_pathes()
        end_of_pathes = 0
        self.serialize_uint_32(end_of_pathes)
        self.serialize_uint_8(SERIALIZATION_COMPLETE)
        self.serialize_object(objects)
        if hasattr(objects, "extra_fields"):
            self.data += objects.extra_fields
        return self.data

    def init_ids(self, o):
        self.ids.clear()
        self.max_new_id = 0
        self.find_ids(o)

    def find_ids(self, o):
        if hasattr(o, "id"):
            self.ids.add(o.id)
        for f in dir(o):
            if not f[0:2] == "__" and hasattr(o, "__dict__") and f in o.__dict__:
                v = o.__dict__[f]
                if hasattr(v, "__iter__"):
                    for i in v:
                        self.find_ids(i)

    def new_id(self):
        id = self.max_new_id + 1
        while id in self.ids:
            id += 1
        self.ids.add(id)
        self.max_new_id = id
        return id

    def serialize_object(self, o):
        class_name = o.__class__.__name__
        if "id" in dir(o):
            if o.id == 0:
                o.id = self.new_id()
            object_id = o.id
        else:
            object_id = 0
        if class_name not in classes.all_classes_by_name:
            raise SerializerError(message.UNKNOWN_CLASS_NAME % class_name)
        (class_id, class_fields_by_name, class_namespace) = classes.all_classes_by_name[
            o.__class__.__name__
        ]
        namespace_id = classes.all_namespaces_by_name[class_namespace]
        self.serialize_uint_32(namespace_id)
        self.serialize_uint_32(class_id)
        self.serialize_uint_32(object_id)
        self.serialize_content(o, class_fields_by_name)

    def serialize_content(self, o, class_fields_by_name):
        for field_name in dir(o):
            if field_name[0:1] == "_":
                continue
            if field_name not in class_fields_by_name:
                continue
            (field_id, field_type) = class_fields_by_name[field_name]
            field_value = getattr(o, field_name)
            if field_value == None:
                continue
            if type(field_type) == tuple:
                (field_type, content_type) = field_type
            if field_type == t_list:
                if len(field_value) > 0:
                    self.serialize_uint_16(field_id)
                    self.serialize_uint_16(field_type)
                    self.serialize_list(field_value, content_type)

            elif field_type == t_direct_reference:
                self.serialize_uint_16(field_id)
                self.serialize_uint_16(field_type)
                self.serialize_object(field_value)

            else:
                self.serialize_uint_16(field_id)
                self.serialize_uint_16(field_type)
                try:
                    self.serialize_value(field_value, field_type)
                except SerializerError:
                    raise SerializerError(
                        message.BAD_FIELD_VALUE
                        % (str(field_value), field_name, t_names[field_type])
                    )
        end_of_fields = 0
        self.serialize_uint_16(end_of_fields)

    def serialize_list(self, list, item_type):
        for item in list:
            self.serialize_object(item)
        end_of_list = 0
        self.serialize_uint_32(end_of_list)

    def serialize_value(self, field_value, field_type):
        localy_defined = 1
        if field_type > 100:
            self.serialize_uint_8(localy_defined)
            if field_type == 107:
                field_type = 8
            else:
                field_type -= 100
        if field_type == t_uint_64:
            self.serialize_uint_64(field_value)
        elif field_type == t_uint_32 or field_type == t_internal_reference:
            self.serialize_uint_32(field_value)
        elif field_type == t_int_32:
            self.serialize_int_32(field_value)
        elif field_type == t_real:
            self.serialize_real(field_value)
        elif field_type == t_boolean:
            self.serialize_boolean(field_value)
        elif (
            field_type == t_string
            or field_type == t_ecma_expression
            or field_type == t_ecma_instruction
        ):
            self.serialize_string(field_value)
        elif field_type == t_external_reference:
            self.serialize_string(field_value)
            index = 0
            self.serialize_uint_32(index)
        elif field_type == t_date:
            self.serialize_date(field_value)
        else:
            raise SerializerError(message.UNKNOWN_FIELD_TYPE % str(field_type))

    def serialize_boolean(self, boolean):
        self.serialize_uint_8(int(bool(boolean)))

    def serialize_uint_8(self, integer, buffer=None):
        if buffer == None:
            self.data.append(integer & 0xFF)
        else:
            buffer.append(integer & 0xFF)

    def serialize_uint_16(self, integer, buffer=None):
        self.serialize_uint_8(integer, buffer)
        self.serialize_uint_8(integer >> 8, buffer)

    def serialize_uint_32(self, integer, buffer=None):
        self.serialize_uint_16(integer, buffer)
        self.serialize_uint_16(integer >> 16, buffer)

    def serialize_int_32(self, integer):
        if integer < 0:
            integer += 0x100000000
        self.serialize_uint_16(integer)
        self.serialize_uint_16(integer >> 16)

    def serialize_uint_64(self, integer):
        self.serialize_uint_32(integer)
        self.serialize_uint_32(integer >> 32)

    def serialize_real(self, real):
        if real == 0.0:
            self.serialize_uint_8(0)
        else:
            realString = str(real)
            self.serialize_uint_8(len(realString))
            for character in realString:
                self.serialize_uint_8(ord(character))

    def serialize_string(self, string, buffer=None):
        if string == None:
            self.serialize_uint_32(0xFFFFFFFF, buffer)
        else:
            self.serialize_uint_32(len(string), buffer)
            for character in string:
                self.serialize_uint_8(ord(character), buffer)

    def serialize_date(self, d):
        if d is None:
            seconds = 0
        else:
            seconds = int(mktime(d.timetuple()))
            self.serialize_uint_32(seconds)
            self.serialize_uint_32(0)
            self.serialize_uint_32(0)

    def serialize_xml(self, objects):
        self.indent = 0
        header = '<?xml version = "1.0" encoding = "ISO-8859-1" standalone = "yes"?>\n'
        class_id, class_fields, self.namespace = classes.all_classes_by_name[
            objects.__class__.__name__
        ]
        content = self.serialize_xml_object_content(
            self.namespace + "." + objects.__class__.__name__, objects
        )
        return header + content

    def serialize_xml_object_content(self, tag_name, objects):
        object_begin_tag = ("\t" * self.indent) + "<" + tag_name
        if len(self.namespace) > 14 and self.namespace[0:13] == "com.consistent":
            if objects.id > 0:
                object_begin_tag += ' id = "_' + str(objects.id) + '"'
        else:
            if str(objects.id) != "0":
                object_begin_tag += ' id = "' + str(objects.id) + '"'
        self.indent += 1
        object_content = ""
        for field_name in dir(objects):
            if field_name[0:2] == "__":
                continue
            if field_name == "id":
                continue
            field = getattr(objects, field_name)
            if field is None:
                continue
            if type(field) is list:
                if len(field) == 0:
                    continue
                if type(field[0]) is int:
                    continue  # Cas des extra_fields : pas de representation xml
                object_content += ("\t" * self.indent) + "<" + field_name + ">\n"
                self.indent += 1
                for item in field:
                    object_content += " " + self.serialize_xml_object_content(
                        item.__class__.__name__, item
                    )
                self.indent -= 1
                object_content += ("\t" * self.indent) + "</" + field_name + ">\n"
            elif type(field) is type:
                object_content += self.serialize_xml_object_content(field_name, field)
            else:
                if "\n" in str(field):
                    object_content += ("\t" * self.indent) + "<" + field_name + ">\n"
                    object_content += ("\t" * self.indent) + "<![CDATA[" + str(field)
                    object_content += ("\t" * self.indent) + "]]>\n"
                    object_content += ("\t" * self.indent) + "</" + field_name + ">\n"
                else:
                    object_begin_tag += " " + field_name + ' = "' + str(field) + '"'

        self.indent -= 1
        if object_content == "":
            return object_begin_tag + " />\n"
        object_begin_tag += " >"
        object_end_tag = ("\t" * self.indent) + "</" + tag_name + ">"
        return object_begin_tag + "\n" + object_content + "\n" + object_end_tag + "\n"


class SerializeMethod(object):
    def __init__(self, module_id, args):
        self.data = [0, 0, 0, 0]
        method_id = args[0]
        self.add_uint_32(method_id)
        self.fns = {
            t_boolean: self.add_boolean,
            t_uint_8: self.add_uint_8,
            t_uint_16: self.add_uint_16,
            t_uint_32: self.add_uint_32,
            t_uint_64: self.add_uint_64,
            t_int_32: self.add_int_32,
            t_string: self.add_string,
            t_real: self.add_real,
            t_date: self.add_date,
            t_data: self.add_data,
            t_object: self.add_object,
            t_any_object: self.add_any_object,
        }
        method_args_types = methods.all_methods_by_id[module_id][method_id][1]
        try:
            if len(args) > 1:
                i = 1
                for method_arg_type in method_args_types:
                    a = args[i]
                    if type(a) is dict:
                        a = self.to_cst_named_object(a)
                    if type(method_arg_type) is tuple:
                        method_arg_type = method_arg_type[0]
                    self.fns[method_arg_type](a)
                    i += 1
        except KeyError:
            raise SerializerMethodError(
                message.UNKNOWN_FIELD_TYPE % str(method_arg_type)
                + message.TRYING_TO_SERIALIZE % str(args[i])
            )

    def to_cst_named_object(self, d):
        o = new_object("consistent_protocol_named_object")
        for k in d.keys():
            if type(d[k]) is dict:
                v = to_ccxml_objects(d[k])
                v.name = k
            else:
                if type(d[k]) is str:
                    v = new_object("consistent_protocol_named_object_value_string")
                elif type(d[k]) is bool:
                    v = new_object("consistent_protocol_named_object_value_boolean")
                elif type(d[k]) is float:
                    v = new_object("consistent_protocol_named_object_value_number")
                elif type(d[k]) is datetime.datetime:
                    v = new_object("consistent_protocol_named_object_value_date")
                elif type(d[k]) is int:
                    v = new_object("consistent_protocol_named_object_value_int_32")
                else:
                    raise SerializerMethodError(
                        "I don't know how to convert type %s in cst_named_object"
                        % type(d[k]).__name__
                    )
                v.name = k
                v.value = d[k]
            o.values.append(v)
        return o

    def add_boolean(self, boolean):
        if boolean:
            self.add_uint_8(1)
        else:
            self.add_uint_8(0)

    def add_uint_8(self, integer):
        self.data.append(integer & 0xFF)

    def add_uint_16(self, integer):
        self.add_uint_8(integer)
        self.add_uint_8(integer >> 8)

    def add_uint_32(self, integer):
        self.add_uint_16(integer)
        self.add_uint_16(integer >> 16)

    def add_int_32(self, integer):
        if integer < 0:
            integer += 0x100000000
        self.add_uint_16(integer)
        self.add_uint_16(integer >> 16)

    def add_uint_64(self, integer):
        self.add_uint_32(integer)
        self.add_uint_32(integer >> 32)

    def add_string(self, string):
        if string == None:
            self.add_uint_32(0)
        else:
            self.add_uint_32(len(string))
            for character in string:
                self.add_uint_8(ord(character))

    def add_real(self, real):
        if real == 0.0:
            self.add_uint_8(0)
        else:
            realString = str(real)
            self.add_uint_8(len(realString))
            for character in realString:
                self.add_uint_8(ord(character))

    def add_date(self, d):
        self.add_uint_32(int(d.date))
        self.add_uint_32(d.get_micro_second())
        self.add_uint_32(d.time_offset)

    def add_data(self, data):
        self.add_uint_32(len(data))
        for d in data:
            if d.__class__ is str:
                self.add_uint_8(ord(d))
            else:
                self.add_uint_8(d)

    def add_any_object(self, o):
        serializer = Serializer()
        consistent_object_class = serializer.get_object_fullname(o)
        self.add_string(consistent_object_class)
        d = serializer.serialize_cdep_objects(o)
        self.add_data(d)

    def add_object(self, o):
        if o is None:
            return
        serializer = Serializer()
        d = serializer.serialize_cdep_objects(o)
        self.add_data(d)

    def serialize(self):
        return self.data
