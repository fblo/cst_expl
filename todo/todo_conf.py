#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>

# This is the todo list !!
# You have to write the feature, implement it, test it and move the import sys;sys.exit() "cursor"
# to the next one.
# When you finish to implement a module, create the unittest based on the feature list and write
# some examples or documentation...
# Isn't it some effective eXtreme Programming ? No, just the Art of Software Development for Idlers.

import cccp.helper as ccc_helper

serveur = ccc_helper.ccc("10.199.30.200")


print "## 1 ##"
o = serveur.ls("/db/projects/Voyance")
for s in o:
	print s

print "## 2 ##"
contenu = serveur.get("/db/projects/Voyance/Ccxml_Voyance.xml")
print contenu

import sys; sys.exit()
import cccp.conf.ccxml as cc

conf = cc.CcxmlConf(contenu)
#contenu = conf.tostring()
#serveur.put("/db/projects/Voyance/Ccxml_Voyance.xml",contenu)
# Users list
print conf.users
# Index of the amuc user (internal property)
print conf.users['amuc'].idx
# Login of the amuc user 
print conf.users['amuc'].login
# Profiles list
print conf.profiles

# Profile of the amuc user
print conf.users['amuc'].profile
# Indexed list of groups
print conf.groups
# Compute a new id (internal function)
print conf.new_id()
# Add a new group named 'new group' under the group named 'default'
print conf.group_add(name='new group',parent=conf.groups['default'])
# This new group should appear in the groups list
print conf.groups
# get the group named 'default', (default group is created if doesn't exists) (internal function)
print conf.get_default_group()
# Objects are created on the fly, so this is always false (__str__ give somethig like : <ccxml_conf.CcxmlConfGroup object at 0x2b2ea31aafd0>) (internal)
print conf.get_default_group().__str__ == conf.get_default_group().__str__
# But they are inherited from indexed_object which has __eq__ property, so this is true 
print conf.get_default_group() == conf.get_default_group()
# And for group it's equivalent to
print conf.get_default_group().name == conf.get_default_group().name
# which is equivalent to (internal)
print conf.get_default_group().idx == conf.get_default_group().idx
# After so many get_default_group, let's verify that there is still just one
print conf.groups
# User set to default group (default group is created if doesn't exists)
user=conf.user_add(
  		   login='ppic',
		   name='Pablo Picasso',
		   password='ppic',
		   profile=conf.profiles['profil_agent']
		  ) 
print user
print user.profile
print user.profile.name
print conf.users
# All users of the group named 'new group'
print conf.groups['default'].users
print conf.groups['default'].groups
# Add a user to this new group
print conf.groups['new group'].user_add(
					login='sdal',
					name='Salvador Dali',
					password='sdal',
					profile=conf.profiles['profil_agent']
				       )
# Add a new "top" group 
print conf.group_add(name='another new group')

