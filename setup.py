#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

from aioutils import __version__

with open('HISTORY.md') as f:
    history = f.read()

setup(
    name='aioutils',
    version=__version__,
    description='Python3 Asyncio Utils',
    long_description= history,
    author='Jingchao Hu',
    author_email='jingchaohu@gmail.com',
    url='https://github.com/observerss/aioutils',
    packages=['aioutils'],
    license='Apache 2.0',
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
        ],
    )
