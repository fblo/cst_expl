#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>


class id_tree(object):
    def __init__(self, objects):
        self.tree = objects
        self.ids = {}
        self._compute_ids(objects)

    def _compute_ids(self, tree_object):
        for field_name in dir(tree_object):
            if field_name[0:2] == "__":
                continue
            field = getattr(tree_object, field_name)
            if type(field).__name__ == "typed_list":
                for item in field:
                    self._compute_ids(item)
        self.ids[tree_object.id] = tree_object

    def new_id(self):
        max = 0
        for id in self.ids.keys():
            if id > max:
                max = id
        return max + 1

    def findall(self, class_name, tree_object=None, root=True):
        if tree_object == None:
            tree_object = self.tree
        result = []

        for field_name in dir(tree_object):
            if field_name[0:2] == "__":
                continue
            field = getattr(tree_object, field_name)
            if type(field).__name__ == "typed_list":
                for item in field:
                    result += self.findall(class_name, item, False)

        if tree_object.__class__.__name__ == class_name and not root:
            result.append(tree_object)

        return result

    def tostring(self, tree_object=None, ident=0):
        if tree_object == None:
            tree_object = self.tree

        if tree_object.__class__.__name__ == "ccenter_ccxml":
            print("{")

        if "name" in tree_object.__dict__:
            print(
                " " * ident + tree_object.__class__.__name__ + " : " + tree_object.name
            )
        else:
            print(" " * ident + tree_object.__class__.__name__)

        for field_name in dir(tree_object):
            if field_name[0:2] == "__":
                continue
            field = getattr(tree_object, field_name)
            if type(field).__name__ == "typed_list":
                for item in field:
                    self.tostring(item, ident + 1)

        if tree_object.__class__.__name__ == "ccenter_ccxml":
            print("}")
