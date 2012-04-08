# coding: utf-8

"""
Creates a unittest.TestCase for the tests defined in the mustache spec.

"""

# TODO: this module can be cleaned up somewhat.

FILE_ENCODING = 'utf-8'  # the encoding of the spec test files.

yaml = None

try:
    # We try yaml first since it is more convenient when adding and modifying
    # test cases by hand (since the YAML is human-readable and is the master
    # from which the JSON format is generated).
    import yaml
except ImportError:
    try:
        import json
    except:
        # The module json is not available prior to Python 2.6, whereas
        # simplejson is.  The simplejson package dropped support for Python 2.4
        # in simplejson v2.1.0, so Python 2.4 requires a simplejson install
        # older than the most recent version.
        import simplejson as json
    file_extension = 'json'
    parser = json
else:
    file_extension = 'yml'
    parser = yaml


import codecs
import glob
import os.path
import unittest

import pystache
from pystache import common
from pystache.renderer import Renderer
from pystache.tests.common import AssertStringMixin, SPEC_TEST_DIR


def parse(u):
    """
    Parse
    Arguments:

      u: a unicode string.

    """
    # TODO: find a cleaner mechanism for choosing between the two.
    if yaml is None:
        # Then use json.

        # The only way to get the simplejson module to return unicode strings
        # is to pass it unicode.  See, for example--
        #
        #   http://code.google.com/p/simplejson/issues/detail?id=40
        #
        # and the documentation of simplejson.loads():
        #
        #   "If s is a str then decoded JSON strings that contain only ASCII
        #    characters may be parsed as str for performance and memory reasons.
        #    If your code expects only unicode the appropriate solution is
        #    decode s to unicode prior to calling loads."
        #
        return json.loads(u)
    # Otherwise, yaml.

    def code_constructor(loader, node):
        value = loader.construct_mapping(node)
        return eval(value['python'], {})

    yaml.add_constructor(u'!code', code_constructor)
    return yaml.load(u)


# This test case lets us alert the user that spec tests are missing.
class CheckSpecTestsFound(unittest.TestCase):

    def test_spec_tests_found(self):
        if len(spec_paths) > 0:
            return
        raise Exception("Spec tests not found in: %s\n  "
            "Consult the README file on how to add the Mustache spec tests." % repr(SPEC_TEST_DIR))


# TODO: give this a name better than MustacheSpec.
class MustacheSpec(unittest.TestCase, AssertStringMixin):
    pass


def buildTest(testData, spec_filename, parser):
    """
    Arguments:

      parser: the module used for parsing (e.g. yaml or json).

    """

    name = testData['name']
    description  = testData['desc']

    test_name = "%s (%s)" % (name, spec_filename)

    def test(self):
        template = testData['template']
        partials = testData.has_key('partials') and testData['partials'] or {}
        # PyYAML seems to leave ASCII strings as byte strings.
        expected = unicode(testData['expected'])
        data     = testData['data']

        # Convert code strings to functions.
        # TODO: make this section of code easier to understand.
        new_data = {}
        for key, val in data.iteritems():
            if isinstance(val, dict) and val.get('__tag__') == 'code':
                val = eval(val['python'])
            new_data[key] = val

        renderer = Renderer(partials=partials)
        actual = renderer.render(template, new_data)

        # We need to escape the strings that occur in our format string because
        # they can contain % symbols, for example (in delimiters.yml)--
        #
        #   "template: '{{=<% %>=}}(<%text%>)'"
        #
        def escape(s):
            return s.replace("%", "%%")

        subs = [description, template, parser.__version__, str(parser)]
        subs = tuple([escape(sub) for sub in subs])
        # We include the parsing module version info to help with troubleshooting
        # yaml/json/simplejson issues.
        message = """%s

  Template: \"""%s\"""

  %%s

  (using version %s of %s)
  """ % subs

        self.assertString(actual, expected, format=message)

    # The name must begin with "test" for nosetests test discovery to work.
    name =  'test: "%s"' % test_name

    # If we don't convert unicode to str, we get the following error:
    #   "TypeError: __name__ must be set to a string object"
    test.__name__ = str(name)

    return test


spec_paths = glob.glob(os.path.join(SPEC_TEST_DIR, '*.%s' % file_extension))
for path in spec_paths:

    file_name  = os.path.basename(path)

    b = common.read(path)
    u = unicode(b, encoding=FILE_ENCODING)
    spec_data = parse(u)

    tests = spec_data['tests']

    for test in tests:
        test = buildTest(test, file_name, parser)
        setattr(MustacheSpec, test.__name__, test)
        # Prevent this variable from being interpreted as another test.
        del(test)

if __name__ == '__main__':
    unittest.main()
