#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>

from datetime import datetime

from ivcommons.time import UTC

from cccp.protocols import classes, methods
from cccp.protocols.ccc_types import (
    t_boolean,
    t_data,
    t_date,
    t_direct_reference,
    t_ecma_expression,
    t_ecma_instruction,
    t_external_reference,
    t_int_32,
    t_internal_reference,
    t_list,
    t_object,
    t_real,
    t_string,
    t_uint_8,
    t_uint_16,
    t_uint_32,
    t_uint_64,
)
from cccp.protocols.errors import DeserializerError
from cccp.protocols.utils import new_object, typed_list

import cccp.protocols.messages.base as message

SERIALIZATION_COMPLETE = 0


class Deserializer(object):
    def __init__(self, data):
        self.data = data
        self.src = 0

    def skip_pathes(self):
        self.src = 0
        list_reseted = False
        while True:
            path = self.deserialize_string()
            if (path is None) or (path == ""):
                break
            if path == "1":
                list_reseted = True
                path = self.deserialize_string()
                if (path is None) or (path == ""):
                    break
            if list_reseted:
                number = self.deserialize_uint_32()  # NOQA

    def deserialize_cdep_objects(self, create_all_fields=False):
        self.create_all_fields = create_all_fields
        self.skip_pathes()
        return self.deserialize_body()

    def deserialize_body(self):
        if self.src == len(self.data):
            return
        mode_loc = self.deserialize_uint_8()
        if mode_loc == SERIALIZATION_COMPLETE:
            number = self.deserialize_uint_32()  # NOQA

            o = self.deserialize_object()

            if self.src != len(self.data):
                o.extra_fields = self.data[self.src :]
            return o

    def deserialize_object(self):
        class_id = self.deserialize_uint_32()
        object_id = self.deserialize_uint_32()
        if class_id not in classes.all_classes_by_id:  # NOQA
            raise DeserializerError(message.UNKNOWN_CLASS_ID % class_id)
        (class_name, class_fields_by_id, class_namespace) = classes.all_classes_by_id[
            class_id
        ]
        o = new_object(class_name)
        if object_id != 0:
            o.id = object_id
        self.deserialize_content(o, class_fields_by_id)
        if class_name == "consistent_protocol_named_object":
            o = self.from_cst_named_object(o)
        return o

    def from_cst_named_object(self, o):
        d = {}
        for v in o.values:
            n = type(v).__name__
            if n == "consistent_protocol_named_object":
                d[v.name] = self.from_cst_named_object(v)
            else:
                if type(v) is dict:
                    d["noname"] = v
                else:
                    try:
                        e = v.value
                    except:
                        e = None
                    d[v.name] = e
        return d

    def deserialize_content(self, o, class_fields_by_id):
        while True:
            field_id = self.deserialize_uint_16()
            if field_id == 0:
                return

            if field_id == 0xFFFF:
                break

            field_type = self.deserialize_uint_16()
            if field_id not in class_fields_by_id:  # NOQA
                raise DeserializerError(message.UNKNOWN_FIELD_ID % (field_id, type(o)))

            (field_name, field_type) = class_fields_by_id[field_id]
            if type(field_type) == tuple:
                (field_type, content_type) = field_type

            if field_type == t_list:
                field_value = self.deserialize_list(
                    field_name,
                    content_type == "consistent_protocol_named_object_value"
                    or content_type == "consistent_protocol_object_value",
                )

            elif field_type == t_direct_reference:
                object_class_loc_id = self.deserialize_uint_32()
                if object_class_loc_id != 0:
                    field_value = self.deserialize_object()
            else:
                field_value = self.deserialize_value(field_type)
            if self.create_all_fields:
                setattr(o, field_name, field_value)
            elif field_value is not None and field_value != "":
                setattr(o, field_name, field_value)

    def deserialize_list(self, list_name, non_typed):
        if list_name in classes.non_typed_lists or non_typed:
            list = []

        else:
            list = typed_list()

        while True:
            object_class_loc_id = self.deserialize_uint_32()
            if object_class_loc_id == 0:
                break

            try:
                list.append(self.deserialize_object())

            except TypeError:
                print("TypeError on append to " + list_name)

        return list

    def deserialize_value(self, field_type):
        if field_type > 100:
            localy_defined = self.deserialize_uint_8()
            if not localy_defined:
                return

            if field_type == 107:
                field_type = 8

            else:
                field_type -= 100

        if field_type == t_uint_64:
            return self.deserialize_uint_64()

        elif field_type == t_uint_32:
            return self.deserialize_uint_32()

        elif field_type == t_int_32:
            return self.deserialize_int_32()

        elif field_type == t_real:
            return self.deserialize_real()

        elif field_type == t_boolean:
            return self.deserialize_boolean()

        elif field_type == t_string:
            return self.deserialize_string()

        elif field_type == t_ecma_expression:
            return self.deserialize_string()

        elif field_type == t_ecma_instruction:
            return self.deserialize_string()

        elif field_type == t_internal_reference:
            return self.deserialize_uint_32()

        elif field_type == t_external_reference:
            reference = self.deserialize_string()
            index = self.deserialize_uint_32()  # NOQA
            return reference

        elif field_type == t_date:
            return self.deserialize_date()

        else:
            raise DeserializerError(message.UNKNOWN_FIELD_TYPE % field_type)

    def skip_object(self):
        self.perfect = False
        while True:
            field_id = self.deserialize_uint_16()
            if field_id == 0:
                break

            self.skip_value(self.deserialize_uint_16())

    def skip_value(self, field_type):
        self.perfect = False
        if field_type == t_uint_64:
            self.deserialize_uint_64()

        elif field_type == t_uint_32:
            self.deserialize_uint_32()

        elif field_type == t_int_32:
            self.deserialize_int_32()

        elif field_type == t_real:
            self.deserialize_real()

        elif field_type == t_boolean:
            self.deserialize_boolean()

        elif (
            (field_type == t_string)
            or (field_type == t_ecma_expression)
            or (field_type == t_ecma_instruction)
        ):
            self.deserialize_string()

        elif field_type == t_list:
            while True:
                object_class_loc_id = self.deserialize_uint_32()
                if object_class_loc_id == 0:
                    break

                self.deserialize_uint_32()
                self.skip_object()

        else:
            raise DeserializerError(message.UNKNOWN_FIELD_TYPE % field_type)

    def deserialize_boolean(self):
        if self.src + 1 > len(self.data):
            return False

        result = not (self.data[self.src] == 0)
        self.src += 1
        return result

    def deserialize_date(self):
        seconds = self.deserialize_uint_32()
        micro_seconds = self.deserialize_uint_32()
        _time_offset = self.deserialize_uint_32()  # NOQA
        if seconds > 0:
            return datetime.utcfromtimestamp(seconds).replace(
                microsecond=micro_seconds, tzinfo=UTC()
            )

        else:
            return None

    def deserialize_uint_8(self):
        if self.src + 1 > len(self.data):
            return 0

        result = self.data[self.src]
        self.src += 1
        return result

    def deserialize_uint_16(self):
        if self.src + 2 > len(self.data):
            return 0

        result = self.data[self.src]
        self.src += 1
        result += self.data[self.src] << 8
        self.src += 1
        return result

    def deserialize_uint_32(self):
        if self.src + 4 > len(self.data):
            return 0

        result = self.data[self.src]
        self.src += 1
        result += self.data[self.src] << 8
        self.src += 1
        result += self.data[self.src] << 16
        self.src += 1
        result += self.data[self.src] << 24
        self.src += 1
        return result

    def deserialize_int_32(self):
        if self.src + 4 > len(self.data):
            return 0

        result = self.data[self.src]
        self.src += 1
        result += self.data[self.src] << 8
        self.src += 1
        result += self.data[self.src] << 16
        self.src += 1
        result += self.data[self.src] << 24
        self.src += 1
        if result < 0x80000000:
            return result

        else:
            return result - 0x100000000

    def deserialize_uint_64(self):
        if self.src + 8 > len(self.data):
            return 0

        result = self.data[self.src]
        self.src += 1
        result += self.data[self.src] << 8
        self.src += 1
        result += self.data[self.src] << 16
        self.src += 1
        result += self.data[self.src] << 24
        self.src += 1
        result += self.data[self.src] << 32
        self.src += 1
        result += self.data[self.src] << 40
        self.src += 1
        result += self.data[self.src] << 48
        self.src += 1
        result += self.data[self.src] << 56
        self.src += 1

        return result

    def deserialize_real(self):
        stringSize = self.deserialize_uint_8()
        if stringSize == 0 or stringSize + self.src > len(self.data):
            return 0.0

        real = ""
        for i in range(self.src, self.src + stringSize):
            real += chr(self.data[i])

        self.src += stringSize
        return float(real)

    def deserialize_string(self):
        string_size = self.deserialize_uint_32()
        if string_size == 0xFFFFFFFF:
            return None

        if (string_size == 0) or (self.src + string_size > len(self.data)):
            return ""

        string = ""
        for i in range(self.src, self.src + string_size):
            string += chr(self.data[i])

        self.src += string_size
        return string.encode("utf-8")


class DeserializeMethod(object):
    def __init__(self, data, module_id):
        self.size = len(data)
        self.data = data
        self.index = 4
        self.module_id = module_id
        self.fns = {
            t_boolean: self.get_boolean,
            t_uint_8: self.get_uint_8,
            t_uint_16: self.get_uint_16,
            t_uint_32: self.get_uint_32,
            t_uint_64: self.get_uint_64,
            t_int_32: self.get_int_32,
            t_string: self.get_string,
            t_real: self.get_real,
            t_date: self.get_date,
            t_data: self.get_data,
            t_object: self.get_object,
        }

    def deserialize(self, objects_with_all_fields=False):
        self.objects_with_all_fields = objects_with_all_fields
        method_id = self.get_uint_32()
        (method_name, method_args_types) = methods.all_methods_by_id[self.module_id][
            method_id
        ]

        l = []
        for method_arg_type in method_args_types:
            if type(method_arg_type) is tuple:
                method_arg_type = method_arg_type[0]

            l.append(self.fns[method_arg_type]())
        return (method_name, tuple(l))

    def get_boolean(self):
        if self.index >= self.size:
            return False

        self.index += 1
        if self.data[self.index - 1] == 1:
            return True

        else:
            return False

    def get_uint_8(self):
        if self.index >= self.size:
            return False

        self.index += 1
        return self.data[self.index - 1]

    def get_uint_16(self):
        if self.index + 2 > self.size:
            return 0

        result = self.get_uint_8()
        result += self.get_uint_8() << 8
        return result

    def get_uint_32(self):
        if self.index + 4 > self.size:
            return 0

        result = self.get_uint_16()
        result += self.get_uint_16() << 16
        return result

    def get_int_32(self):
        if self.index + 4 > self.size:
            return 0

        result = self.get_uint_16()
        result += self.get_uint_16() << 16
        if result < 0x80000000:
            return result

        else:
            return result - 0x100000000

    def get_uint_64(self):
        if self.index + 8 > self.size:
            return 0

        result = self.get_uint_32()
        result += self.get_uint_32() << 32
        return result

    def get_real(self):
        if self.index >= self.size:
            return 0.0

        stringSize = self.get_uint_8()
        if stringSize == 0 or stringSize + self.index > self.size:
            return 0.0

        real = ""
        for i in range(self.index, self.index + stringSize):
            real += chr(self.data[i])

        self.index += stringSize
        return float(real)

    def get_string(self):
        if self.index + 4 > self.size:
            return ""

        stringSize = self.get_uint_32()
        if stringSize == 0 or stringSize + self.index > self.size:
            return ""

        string = ""
        for i in range(self.index, self.index + stringSize):
            string += chr(self.data[i])

        self.index += stringSize
        return string.encode("utf-8")

    def get_data(self):
        if self.index + 4 > self.size:
            return None

        dataSize = self.get_uint_32()
        if dataSize + self.index > self.size:
            return None

        data = self.data[self.index : self.index + dataSize]
        self.index += dataSize
        return data

    def get_date(self):
        seconds = self.get_uint_32()
        micro_seconds = self.get_uint_32()
        _time_offset = self.get_int_32()  # NOQA
        if seconds > 0:
            return datetime.utcfromtimestamp(seconds).replace(
                microsecond=micro_seconds, tzinfo=UTC()
            )

        else:
            return None

    def get_object(self):
        deserializer = Deserializer(self.get_data())
        return deserializer.deserialize_cdep_objects(
            create_all_fields=self.objects_with_all_fields
        )
