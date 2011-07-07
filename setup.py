#!/usr/bin/env python
from setuptools import setup, find_packages

# Todo: Add dependency for virtualboxapi
# Todo: Sync verion here with version in util/pyvbox.py
setup(
    name = "pyPerspectives",
    version = "0.1",
    packages = find_packages(),
    scripts = ['utils/notary-query.py'],
    test_suite = 'unittests',

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A python Perspectives (http://perspectives-project.org/) client library",
    license = "Apache2",
    url = "https://github.com/von/pyPerspectives"
)
