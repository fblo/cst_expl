#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
# - PEMO <pemo@interact-iv.com>
# - SLAU <slau@interact-iv.com>

import unittest
from cccp.sync.db import ConfigDB
from cccp.conf.ccxml import CcxmlConf
from cccp.protocols.errors import CcxmlConfError
from test_configuration import *


class test_CcxmlConf(unittest.TestCase):
    def setUp(self):
        global CCC_IP
        global CCC_PROJECT_NAME
        contenu = ConfigDB(CCC_IP).get(
            CDB_PROJECTS_PATH + "/" + CCC_PROJECT_NAME + "/" + CONF_CCXML_NAME
        )
        self.conf = CcxmlConf(contenu)

    def test_group_add(self):
        avant = len(self.conf.groups)
        # Add a new group named 'new group' under the group named 'default'
        self.assertRaises(CcxmlConfError, self.conf.group_add, CONF_DEFAULT_GROUP_NAME)
        self.conf.group_add(
            name="new group", parent=self.conf.groups[CONF_DEFAULT_GROUP_NAME]
        )

        # This new group should appear in the groups list
        self.assertEqual(self.conf.groups["new group"].name, "new group")

        self.assertTrue(len(self.conf.groups[CONF_DEFAULT_GROUP_NAME].groups) == 1)
        self.assertTrue(len(self.conf.groups) == avant + 1)
        # Add a new "top" group
        self.conf.group_add(name="another new group")
        self.assertTrue(len(self.conf.groups) == avant + 2)

    def test_user_add(self):
        avant = len(self.conf.users)
        self.conf.groups[CONF_DEFAULT_GROUP_NAME].user_add(
            login="amuc",
            name="Alfons Mucha",
            password="amuc",
            profile=self.conf.profiles[CONF_DEFAULT_AGENT_PROFILE_NAME],
        )
        # User set to default group (default group is created if doesn't exists)
        user = self.conf.user_add(
            login="ppic",
            name="Pablo Picasso",
            password="ppic",
            profile=self.conf.profiles[CONF_DEFAULT_AGENT_PROFILE_NAME],
        )
        self.assertTrue(len(self.conf.users) == avant + 1)
        self.assertEqual(user.profile.name, CONF_DEFAULT_AGENT_PROFILE_NAME)
        self.assertEqual(user.name, self.conf.users["ppic"].name)

        # Add a user to the new group
        self.conf.group_add(
            name="new group", parent=self.conf.groups[CONF_DEFAULT_GROUP_NAME]
        )
        self.conf.groups["new group"].user_add(
            login="sdal",
            name="Salvador Dali",
            password="sdal",
            profile=self.conf.profiles[CONF_DEFAULT_AGENT_PROFILE_NAME],
        )
        # What happens if the user already exists ?

    def test_users_list(self):
        # Users list
        self.assertFalse(self.conf.users is None)
        # All users of the group named 'new group'
        self.assertFalse(self.conf.groups[CONF_DEFAULT_GROUP_NAME].users is None)

    def test_profiles_list(self):
        # Profiles list
        self.assertFalse(self.conf.profiles is None)
        # Profile of the amuc user
        self.assertFalse(self.conf.users["amuc"].profile is None)

    def test_groups_list(self):
        # Indexed list of groups
        self.assertFalse(self.conf.groups is None)

    def test_new_id(self):
        # Compute a new id (internal function)
        self.assertTrue(self.conf.new_id() > 0)

    def test_default_group(self):
        # get the group named 'default', (default group is created if doesn't exists) (internal function)
        self.assertFalse(self.conf.get_default_group() is None)

    def test_indexed_object_equality(self):
        # Objects are created on the fly, but __str__ return json like objects
        self.assertTrue(
            self.conf.get_default_group().__str__
            == self.conf.get_default_group().__str__
        )
        # But they are inherited from indexed_object which has __eq__ property, so this is true
        self.assertTrue(self.conf.get_default_group() == self.conf.get_default_group())
        # And for group it's equivalent to
        self.assertTrue(
            self.conf.get_default_group().name == self.conf.get_default_group().name
        )
        # which is equivalent to (internal)
        self.assertTrue(
            self.conf.get_default_group().idx == self.conf.get_default_group().idx
        )

    def test_user_idx(self):
        # Index of the amuc user (internal property)
        self.assertEqual(self.conf.users["amuc"].idx, "amuc")
        self.assertEqual(self.conf.users["amuc"].login, "amuc")
        self.assertEqual(self.conf.users["amuc"].login, self.conf.users["amuc"].idx)
