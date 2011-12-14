# coding: utf-8

"""
This module provides command-line access to pystache.

Run this script using the -h option for command-line help.

"""

# TODO: allow option parsing to work in Python versions earlier than
# Python 2.7 (e.g. by using the optparse module).  The argparse module
# isn't available until Python 2.7.
import argparse
import json

# We use absolute imports here to allow use of this script from its
# location in source control (e.g. for development purposes).
# Otherwise, the following error occurs:
#
#   ValueError: Attempted relative import in non-package
#
from pystache.loader import Loader
from pystache.template import Template


def main():
    parser = argparse.ArgumentParser(description='Render a mustache template with the given context.')
    parser.add_argument('template',  help='A filename or a template code.')
    parser.add_argument('context', help='A filename or a JSON string')
    args = parser.parse_args()

    if args.template.endswith('.mustache'):
        args.template = args.template[:-9]

    try:
        template = Loader().load_template(args.template)
    except IOError:
        template = args.template

    try:
        context = json.load(open(args.context))
    except IOError:
        context = json.loads(args.context)

    print(Template(template, context).render())


if __name__=='__main__':
    main()

