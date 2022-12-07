#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU Lesser General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (LGPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of LGPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/lgpl-2.0.txt.
#
# Jeff Ortel <jortel@redhat.com>
#

from setuptools import setup, find_packages

setup(
    name='katello-host-tools',
    version='4.2.3',
    description='Libraries and command-line utilities for keeping Katello clients in sync and up to date',
    author='The Foreman Project',
    author_email='no-email@theforeman.org',
    url='https://github.com/Katello/katello-host-tools',
    license='GPLv2+',
    packages=find_packages(),
    include_package_data=False,
    package_data={ '': [ '../katello/contrib/etc/*/*/*.conf', '../katello/contrib/extra/*' ] },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'katello-enabled-repos-upload=katello.scripts:enabled_repos_upload',
            'katello-package-upload=katello.scripts:package_upload',
            'katello-tracer-upload=katello.scripts:tracer_upload',
        ],
    },
)
