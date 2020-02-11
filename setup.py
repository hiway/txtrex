#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function
)

import io
import re
from glob import glob
from os.path import (
    basename,
    dirname,
    join,
    splitext
)

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='txtrex',
    version='0.1.0',
    license='Apache License 2.0',
    description='Publish a "blog" using DNS TXT records.',
    author='Harshad Sharma',
    author_email='harshad@sharma.io',
    url='https://github.com/hiway/txtrex',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    keywords=[
    ],
    install_requires=[
        'arrow',
        'twisted'
    ],
    entry_points={
        'console_scripts': [
            'txtrex = txtrex.txtrex:main',
        ]
    },
)
