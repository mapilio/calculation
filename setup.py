#!/usr/bin/env python
"""
Mapilio Calculation
"""
from __future__ import (absolute_import, division, print_function)

import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 5):
    raise RuntimeError(
        "Mapilio Calculation supports Python 3.6 and above. "
    )

# This import must be below the above `sys.version_info` check,
# because the code being imported here is not compatible with the older
# versions of Python.
from increment_version import __version__
from calculation.util import __name__

INSTALL_REQUIRES = [
    'numpy',
    'solve',
    'trianglesolver',
    'geopy',
    'helper-mapilio',
    'scipy'
]

setup(
    name=__name__,
    version=__version__,
    description='Mapilio Calculation Library',
    url='https://github.com/mapilio/calculation.git',
    author='Mapilio - Ozcan Durak & MCV',
    author_email='ozcan@visiosoft.com.tr',
    license='licensed',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.6, <4",
    project_urls={  # Optional
            'Bug Reports': 'https://github.com/mapilio/calculation/issues',
            'Say Thanks!': 'https://mapilio.com/#contact',
            'Source': 'https://github.com/mapilio/calculation/',
        },
)