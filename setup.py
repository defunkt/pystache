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
      version='0.3.0',
      description='Mustache for Python',
      long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
      author='Chris Wanstrath',
      author_email='chris@ozmm.org',
      url='http://github.com/defunkt/pystache',
      packages=['pystache'],
      license='MIT',
      classifiers = ( 
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        )
     )

