# coding: utf-8

"""
Tests the mustache spec test cases.

"""

import glob
import os.path
import unittest
import yaml

import pystache
from pystache import Loader


def code_constructor(loader, node):
    value = loader.construct_mapping(node)
    return eval(value['python'], {})

yaml.add_constructor(u'!code', code_constructor)

specs = os.path.join(os.path.dirname(__file__), '..', 'ext', 'spec', 'specs')
specs = glob.glob(os.path.join(specs, '*.yml'))

class MustacheSpec(unittest.TestCase):
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
        files    = []

        try:
            for key in partials.keys():
                filename = "%s.%s" % (key, Loader.template_extension)
                files.append(os.path.join(Loader.template_path, filename))
                p = open(files[-1], 'w')
                p.write(partials[key])
                p.close()
            actual = pystache.render(template, data).encode('utf-8')

            message = """%s

  Template: \"""%s\"""

  Expected: %s
  Actual:   %s""" % (description, template, repr(expected), repr(actual))

            self.assertEquals(actual, expected, message)
        finally:
            [os.remove(f) for f in files]

    # The name must begin with "test" for nosetests test discovery to work.
    test.__name__ = 'test: "%s"' % test_name

    return test

for spec in specs:
    file_name  = os.path.basename(spec)

    for test in yaml.load(open(spec))['tests']:
        test = buildTest(test, file_name)
        setattr(MustacheSpec, test.__name__, test)

if __name__ == '__main__':
    unittest.main()
