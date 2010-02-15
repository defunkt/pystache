#!/usr/bin/env python

import os
import sys

from distutils.core import setup

def publish():
    """Publish to Pypi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(name='pystache',
      version='0.2.0',
      description='Mustache for Python',
      author='Chris Wanstrath',
      author_email='chris@ozmm.org',
      url='http://github.com/defunkt/pystache',
      packages=['pystache'],
      license='MIT'
     )

