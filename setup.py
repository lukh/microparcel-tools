#!/usr/bin/env python
# -*- coding: utf-8 -*-

from microparcel_tools import __version__

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "Cerberus",
    'jsoncomment',
    'jinja2'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Vivien Henry",
    author_email='vivien.henry@outlook.fr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Code generation tool for microparcel",
    entry_points={
        'console_scripts': [
            'microparcel_tools=microparcel_tools.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='microparcel_tools',
    name='microparcel_tools',
    packages=find_packages(include=['microparcel_tools']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lukh/microparcel-tools',
    version=__version__,
    zip_safe=False,
)
