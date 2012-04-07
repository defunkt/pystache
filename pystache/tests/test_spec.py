# coding: utf-8

"""
Creates a unittest.TestCase for the tests defined in the mustache spec.

"""

# TODO: this module can be cleaned up somewhat.

FILE_ENCODING = 'utf-8'  # the encoding of the spec test files.


try:
    # We use the JSON files rather than the YAML files because json libraries
    # are available for Python 2.4.
    import json
except:
    # The module json is not available prior to Python 2.6, whereas simplejson is.
    # Note that simplejson dropped support for Python 2.4 in simplejson v2.1.0,
    # so Python 2.4 requires a simplejson install older than the most recent.
    import simplejson as json

import glob
import os.path
import unittest

import pystache
from pystache.renderer import Renderer
from pystache.tests.common import AssertStringMixin, SPEC_TEST_DIR


spec_paths = glob.glob(os.path.join(SPEC_TEST_DIR, '*.json'))


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


def buildTest(testData, spec_filename):

    name = testData['name']
    description  = testData['desc']

    test_name = "%s (%s)" % (name, spec_filename)

    def test(self):
        template = testData['template']
        partials = testData.has_key('partials') and testData['partials'] or {}
        expected = testData['expected']
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

        subs = [description, template, json.__version__, str(json)]
        subs = tuple([escape(sub) for sub in subs])
        # We include the json module version to help in troubleshooting
        # json/simplejson issues.
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


for spec_path in spec_paths:

    file_name  = os.path.basename(spec_path)

    # We avoid use of the with keyword for Python 2.4 support.
    f = open(spec_path, 'r')
    try:
        s = f.read()
    finally:
        f.close()

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
    u = s.decode(FILE_ENCODING)
    spec_data = json.loads(u)

    tests = spec_data['tests']

    for test in tests:
        test = buildTest(test, file_name)
        setattr(MustacheSpec, test.__name__, test)
        # Prevent this variable from being interpreted as another test.
        del(test)

if __name__ == '__main__':
    unittest.main()
