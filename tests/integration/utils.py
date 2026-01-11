#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>

def print_list(l,name):
	if not PRINT_MODE: 
		return
	print 
	print "--"+name+"-- :"
	for o in l:
		print o.name

def find_by_name(l,name):
	for o in l:
		if o.name == name:
			return True
	return False

