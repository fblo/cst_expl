#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

import cccp.land.idx as il
from cccp.land.tree import id_tree
from cccp.protocols.utils import new_object
from cccp.protocols.errors import CcxmlConfError
import cccp.protocols.messages.base as message


class User(il.indexed_object):
    # Construction possible from ccc_object
    def __init__(self, ccc_object, ccxml_conf):
        il.indexed_object.__init__(self, self.get_login, self.set_login)
        self.ccc_object = ccc_object
        self.ccxml_conf = ccxml_conf

    def get_login(self):
        return self.ccc_object.login

    def set_login(self, value):
        old_value = self.ccc_object.login
        self.ccc_object.login = value
        self.set_dict_idx(old_value)

    login = property(get_login, set_login)

    def get_profile(self):
        return Profile(self.ccxml_conf.ids[self.ccc_object.profile])

    def set_profile(self, value):
        # TODO: Check the existence of the id in the ids dict and the type of the object associated with.
        self.ccc_object.profile = value.ccc_object.id

    profile = property(get_profile, set_profile)

    def get_name(self):
        return self.ccc_object.name

    def set_name(self, value):
        self.ccc_object.name = value

    name = property(get_name, set_name)


class Profile(il.indexed_object):
    # Construction possible from ccc_object
    def __init__(self, ccc_object):
        il.indexed_object.__init__(self, self.get_name, self.set_name)
        self.ccc_object = ccc_object

    def get_name(self):
        return self.ccc_object.name

    def set_name(self, value):
        old_value = self.ccc_object.name
        self.ccc_object.name = value
        self.set_dict_idx(old_value)

    name = property(get_name, set_name)


class Group(il.indexed_object):
    # Construction possible from ccc_object
    def __init__(self, ccc_object, ccxml_conf):
        il.indexed_object.__init__(self, self.get_name, self.set_name)
        self.ccc_object = ccc_object
        self.ccxml_conf = ccxml_conf

    def get_name(self):
        return self.ccc_object.name

    def set_name(self, value):
        old_value = self.ccc_object.name
        self.ccc_object.name = value
        self.set_dict_idx(old_value)

    name = property(get_name, set_name)

    def get_users(self):
        result = il.indexed_objects_dict()
        for ccc_object in self.ccxml_conf.findall("ccenter_ccxml_user"):
            result.add(User(ccc_object, self))
        return result

    users = property(
        get_users,
    )

    def get_groups(self):
        result = il.indexed_objects_dict()
        for ccc_object in self.ccxml_conf.findall(
            "ccenter_ccxml_group", self.ccc_object
        ):
            result.add(Group(ccc_object, self.ccxml_conf))
        return result

    groups = property(
        get_groups,
    )

    def user_add(self, login, name, password, profile):
        new_user = new_object("ccenter_ccxml_user")
        new_user.id = self.ccxml_conf.new_id()
        new_user.login = login
        new_user.name = name
        new_user.password = password
        new_user.profile = profile.ccc_object.id
        self.ccc_object.users.append(new_user)
        self.ccxml_conf.ids[new_user.id] = new_user
        return User(new_user, self.ccxml_conf)


class CcxmlConf(id_tree):
    def __init__(self, objects):
        id_tree.__init__(self, objects)

    def get_users(self):
        result = il.indexed_objects_dict()
        for ccc_object in self.findall("ccenter_ccxml_user"):
            result.add(User(ccc_object, self))
        return result

    users = property(
        get_users,
    )

    def get_profiles(self):
        result = il.indexed_objects_dict()
        for ccc_object in self.findall("ccenter_ccxml_profile"):
            result.add(Profile(ccc_object))
        return result

    profiles = property(
        get_profiles,
    )

    def get_groups(self):
        result = il.indexed_objects_dict()
        for ccc_object in self.findall("ccenter_ccxml_group"):
            result.add(Group(ccc_object, self))
        return result

    groups = property(
        get_groups,
    )

    def get_default_group(self):
        result = None
        for ccc_object in self.findall("ccenter_ccxml_group"):
            if ccc_object.name == "default_group":
                result = Group(ccc_object, self)
                break
        if result is None:
            result = self.group_add("default_group", "default_group")
        return result

    def user_add(self, login, name, password, profile):
        ccc_object = self.get_default_group().ccc_object
        new_user = new_object("ccenter_ccxml_user")
        new_user.id = self.new_id()
        new_user.login = login
        new_user.name = name
        new_user.password = password
        new_user.profile = profile.ccc_object.id
        ccc_object.users.append(new_user)
        self.ids[new_user.id] = new_user
        return User(new_user, self)

    def group_add(self, name, display_name="", parent=None):
        if parent.__class__ is Group:
            ccc_object = parent.ccc_object
        else:
            ccc_object = self.tree
        for group in ccc_object.groups:
            if group.name == name:
                raise CcxmlConfError(message.GROUP_EXISTS % name)
        new_group = new_object("ccenter_ccxml_group")
        new_group.id = self.new_id()
        new_group.name = name
        new_group.display_name = display_name

        ccc_object.groups.append(new_group)
        self.ids[new_group.id] = new_group

        return Group(new_group, self)
