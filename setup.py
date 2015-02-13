#!/usr/bin/env python
from distutils.core import setup
import sys

long_description = ''

if 'upload' in sys.argv:
    with open('README.rst') as f:
        long_description = f.read()

version_info = sys.version_info

setup(
    name='metautils',
    version='0.1.0',
    description='Utilities for working with metaclasses',
    author='Joe Jevnik',
    author_email='joe@quantopian.com',
    packages=[
        'metautils',
    ],
    long_description=long_description,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    url='https://github.com/llllllllll/metautils',
    install_requires=(
        'functools32',
    ) if version_info.major == 2 and version_info == 7 else (),
)
