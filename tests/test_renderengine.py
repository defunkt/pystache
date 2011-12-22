# coding: utf-8

"""
Unit tests of renderengine.py.

"""

import cgi
import unittest

from pystache.context import Context
from pystache.renderengine import RenderEngine


class RenderEngineTestCase(unittest.TestCase):

    """Test the RenderEngine class."""

    def test_render(self):
        escape = lambda s: cgi.escape(unicode(s))
        engine = RenderEngine(literal=unicode, escape=escape)
        context = Context({'person': 'Mom'})
        actual = engine.render('Hi {{person}}', context)
        self.assertEquals(actual, 'Hi Mom')
