#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

from aiopool import __version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.md') as f:
    readme = f.read()

with open('HISTORY.md') as f:
    history = f.read()

setup(
    name='aiopool',
    version=__version__,
    description='Gevent Pool and Group alike in Python3 Asyncio',
    long_description=readme + '\n\n' + history,
    author='Jingchao Hu',
    author_email='jingchaohu@gmail.com',
    url='https://github.com/observerss/aiopool',
    packages=['aiopool'],
    license='Apache 2.0',
    zip_safe=True,
    # classifiers=(
        # 'Development Status :: 5 - Production/Stable',
        # 'Intended Audience :: Developers',
        # 'Natural Language :: English',
        # 'License :: OSI Approved :: Apache Software License',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4'
        # ),
    )
