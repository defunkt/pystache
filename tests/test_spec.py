import glob
import os.path
import pystache
import unittest
import yaml

def code_constructor(loader, node):
    value = loader.construct_mapping(node)
    return eval(value['python'], {})

yaml.add_constructor(u'!code', code_constructor)

specs = os.path.join(os.path.dirname(__file__), '..', 'ext', 'spec', 'specs')
specs = glob.glob(os.path.join(specs, '*.yml'))

class MustacheSpec(unittest.TestCase):
    pass

def buildTest(testData, spec):
    def test(self):
        template = testData['template']
        partials = testData.has_key('partials') and test['partials'] or {}
        expected = testData['expected']
        data     = testData['data']
        self.assertEquals(pystache.render(template, data), expected)

    test.__doc__  = testData['desc']
    test.__name__ = 'test %s (%s)' % (testData['name'], spec)
    return test

for spec in specs:
    name  = os.path.basename(spec).replace('.yml', '')

    for test in yaml.load(open(spec))['tests']:
        test = buildTest(test, name)
        setattr(MustacheSpec, test.__name__, test)

if __name__ == '__main__':
    unittest.main()
