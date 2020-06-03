#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup
import os

__version__ = '0.1.1'  # Should match with __init.py__
_PACKAGE_NAME = 'trainline'
_GITHUB_URL = 'https://github.com/tducret/trainline-python'
_KEYWORDS = ['api', 'trainline', 'parsing', 'train', 'sncf',
             'python-wrapper', 'scraping', 'scraper', 'parser']
_SCRIPTS = ['trainline_cli.py']
_PACKAGE_DATA = ['stations_mini.csv']

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def parse_requirements(filepath):
    """ load requirements from a pip requirements file. """
    with open(filepath) as f:
        lines = (line.strip() for line in f)
        return [line for line in lines if line and not line.startswith('#')]

requirements = parse_requirements(os.path.join(ROOT_DIR, 'requirements.txt'))

setup(
    name=_PACKAGE_NAME,
    packages=[_PACKAGE_NAME],
    package_data={_PACKAGE_NAME: _PACKAGE_DATA, },
    scripts=_SCRIPTS,
    version=__version__,
    license="MIT license",
    platforms='Posix; MacOS X',
    description="Non-official Python wrapper and CLI tool for Trainline",
    long_description="Non-official Python wrapper and CLI tool for Trainline",
    author="Thibault Ducret",
    author_email='hello@tducret.com',
    url=_GITHUB_URL,
    download_url='{github_url}/tarball/{version}'.format(
                                                github_url=_GITHUB_URL,
                                                version=__version__),
    keywords=_KEYWORDS,
    setup_requires=requirements,
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3',
    tests_require=['pytest'],
)

# ------------------------------------------
# To upload a new version on pypi
# ------------------------------------------
# Make sure everything was pushed (with a git status)
# (or git commit --am "Comment" and git push)
# export VERSION=0.1.1; git tag $VERSION -m "Change user-agent to avoid error 400 (issue #11)"; git push --tags

# If you need to delete a tag
# git push --delete origin $VERSION; git tag -d $VERSION
