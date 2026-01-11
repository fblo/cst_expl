#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>

from cccp.protocols.ccc_types import t_list
from cccp.protocols.classes import all_classes_by_name


# Dynamic type creation with instanciation of the list type fields
class typed_list(list):
    content_type = ""

    def append(self, item):
        if self.content_type == "":
            self.content_type = type(item).__name__
        else:
            if type(item).__name__ != self.content_type:
                if type(item).__name__.find(self.content_type) == -1:
                    raise TypeError
        list.append(self, item)

    def __str__(self):
        s = "[\n"
        first_object = True
        for e in self:
            if not first_object:
                s += ", \n"
            s += print_object(e, 1)
        s += "]"
        return s


def print_object(o, i=0):
    s = "%s{\n" % ("\t" * i)
    i += 1
    first_field = True
    for f in sorted(o.__dict__):
        if f == "requester":
            continue

        if not first_field:
            s += ", \n"

        s += "%s'%s':" % ("\t" * i, f)
        v = o.__dict__[f]
        if type(v).__name__ == "typed_list" or type(v).__name__ == "list":
            first_object = True
            s += " [\n"

            for e in v:
                if not first_object:
                    s += ", \n"
                s += print_object(e, i + 1)

            s += "%s]" % ("\t" * i)

        else:
            if v is None:
                v = "None"
            elif type(v) is str:
                v = "'%s'" % v
            elif type(v) is int:
                v = str(v)
            elif type(v) is bool:
                v = str(v)
            elif type(v) is float:
                v = str(v)
            elif type(v).__name__ == "datetime":
                v = v.__str__()
            else:
                v = print_object(v)
            s += v

        first_field = False

    i -= 1
    s += "\n%s}\n" % ("\t" * i)
    return s


def new_class(class_name, with_all_fields=False):
    fields = dict(id=0)
    class_id, class_fields_by_name, class_namespace = all_classes_by_name[class_name]

    for field_name in class_fields_by_name:
        field_id, field_type = class_fields_by_name[field_name]

        if type(field_type) == tuple:
            (field_type, content_type) = field_type

        if field_type == t_list:
            fields[field_name] = typed_list()
            fields[
                field_name
            ].content_type = (
                content_type  # TODO : Ajouter le namespace si different du courant.
            )
            continue

        if with_all_fields:
            if type(field_type) is str:
                fields[field_name] = None
                continue

            fields[field_name] = t_default[field_type]

    # fields["__str__"] = lambda s: str(vars(s))
    fields["__str__"] = print_object

    return type(class_name, (object,), fields)


def new_object(class_name, with_all_fields=False):
    t = new_class(class_name, with_all_fields)
    o = t()
    return o
