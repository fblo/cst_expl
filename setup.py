#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""cccp setup script."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='cccp',
    version='1.4.6',
    author='SOFTeam',
    author_email='softeam@interact-iv.com',
    packages=[
        'cccp',
        'cccp.conf',
        'cccp.async',
        'cccp.sync',
        'cccp.protocols',
        'cccp.protocols.clients',
        'cccp.protocols.messages',
        'cccp.protocols.rt',
        'cccp.usage',
        'cccp.land',
        'cccp.tests',
        'cccp.tests.protocols',
        'cccp.tests.protocols.rt',
        'cccp.tests.async'

    ],
    package_dir={
        'cccp': 'src/cccp',
        'cccp.tests': 'tests/unit-tests'
    },
    requires=[
        'pyparsing (>=1.5)'
    ]
)
