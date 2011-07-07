#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "pyPerspectives",
    version = "0.1",
    packages = [ "Perspectives" ],
    scripts = ['utils/notary-query.py'],
    test_suite = 'unittests',

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A python Perspectives (http://perspectives-project.org/) client library",
    license = "Apache2",
    url = "https://github.com/von/pyPerspectives"
)
