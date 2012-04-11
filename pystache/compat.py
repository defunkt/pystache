# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# pythonbackports - support newer code on older Python implementations
# Copyright (C) 2011-2012  Chris Clark
"""New stuff is simply exposed in this module (does not mess with builtins)

So for now simply issue:

    from pystache.compat import *
"""


try:
    basestring
except NameError:
    # probably Python 2.2 or earlier
    basestring = (str, unicode)

try:
    reversed
except NameError:
    # reversed was added in Python 2.4
    # NOTE this is not an iterator/generator...
    def reversed(in_list):
        out_list = []
        for i in range(1, len(in_list) + 1):
            out_list.append(in_list[-1])
        return out_list

try:
    UnicodeDecodeError
    UnicodeEncodeError
except NameError:
    # probably Python 2.2 or earlier
    UnicodeDecodeError = UnicodeError
    UnicodeEncodeError = UnicodeError

try:
    sorted
except NameError:
    # sorted was added in Python 2.4
    def sorted(iterable, cmp=None, key=None, reverse=None):
        if cmp:
            raise NotImplementedError('cmp not yet implemented')
        if key:
            raise NotImplementedError('key not yet implemented')
        if reverse:
            raise NotImplementedError('reverse not yet implemented')
        out_list = list(iterable)[:]
        out_list.sort()
        return out_list
