#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = "pyPerspectives",
    version = "0.4",
    packages = [ "Perspectives" ],
    package_data = { "Perspectives" : [
            "conf/http_notary_list.txt",
            ] },
    scripts = ['utils/notary-query.py'],
    test_suite = 'unittests',

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A python Perspectives (http://perspectives-project.org/) client library",
    license = "Apache2",
    url = "https://github.com/von/pyPerspectives"
)
