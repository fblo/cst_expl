#!/usr/bin/env python

# This file is part of Interact-IV's IV2US Tools.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - SLAU <slau@interact-iv.com>
#    - JTAG <jtag@interact-iv.com>

"""Setup file for iv2us-tools package."""

try:
    from setuptools import setup
    from setuptools.command import egg_info  # NOQA
    from setuptools.command.install import install
except (ImportError, AttributeError):
    from distutils.core import setup
    from distutils.command.install import install  # NOQA

setup(
    name='iv2us-tools',
    version='1.1.14',
    description='Interact-IV IV2US Tools',
    author='SOFTeam',
    author_email='softeam@interact-iv.com',
    scripts=[
        'src/scripts/iv-banners-migrate',
        'src/scripts/iv-clean-entrypoints',
        'src/scripts/iv-fix-1713',
        'src/scripts/iv-force-no-anonymous',
        'src/scripts/iv-import-records',
        'src/scripts/iv-sync',
        'src/scripts/iv-new-project',
        'src/scripts/iv-remove-project',
        'src/scripts/iv-restart-modules',
        'src/scripts/iv-static-ports',
        'src/scripts/iv-sounds-settings',
        'src/scripts/iv-toggle-scheduler',
        'src/scripts/iv-vocal-project-values',
        'src/scripts/sync-vocal-entrypoints',
        'src/scripts/replay_records'
    ],
    packages=[
        'ivsync'
    ],
    package_dir={
        'ivsync': 'src/iv-sync',
    },
    zip_safe=False
)
