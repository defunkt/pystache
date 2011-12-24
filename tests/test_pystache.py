# encoding: utf-8

import unittest
import pystache
from pystache import renderer


class PystacheTests(object):

    """
    Contains tests to run with markupsafe both enabled and disabled.

    To run the tests in this class, this class should be subclassed by
    a class that implements unittest.TestCase.

    """

    def _assert_rendered(self, expected, template, context):
        actual = pystache.render(template, context)
        self.assertEquals(actual, expected)

    def test_basic(self):
        ret = pystache.render("Hi {{thing}}!", { 'thing': 'world' })
        self.assertEquals(ret, "Hi world!")

    def test_kwargs(self):
        ret = pystache.render("Hi {{thing}}!", thing='world')
        self.assertEquals(ret, "Hi world!")

    def test_less_basic(self):
        template = "It's a nice day for {{beverage}}, right {{person}}?"
        ret = pystache.render(template, { 'beverage': 'soda', 'person': 'Bob' })
        self.assertEquals(ret, "It's a nice day for soda, right Bob?")

    def test_even_less_basic(self):
        template = "I think {{name}} wants a {{thing}}, right {{name}}?"
        ret = pystache.render(template, { 'name': 'Jon', 'thing': 'racecar' })
        self.assertEquals(ret, "I think Jon wants a racecar, right Jon?")

    def test_ignores_misses(self):
        template = "I think {{name}} wants a {{thing}}, right {{name}}?"
        ret = pystache.render(template, { 'name': 'Jon' })
        self.assertEquals(ret, "I think Jon wants a , right Jon?")

    def test_render_zero(self):
        template = 'My value is {{value}}.'
        ret = pystache.render(template, { 'value': 0 })
        self.assertEquals(ret, 'My value is 0.')

    def test_comments(self):
        template = "What {{! the }} what?"
        ret = pystache.render(template)
        self.assertEquals(ret, "What  what?")

    def test_false_sections_are_hidden(self):
        template = "Ready {{#set}}set {{/set}}go!"
        ret = pystache.render(template, { 'set': False })
        self.assertEquals(ret, "Ready go!")

    def test_true_sections_are_shown(self):
        template = "Ready {{#set}}set{{/set}} go!"
        ret = pystache.render(template, { 'set': True })
        self.assertEquals(ret, "Ready set go!")

    non_strings_expected = """(123 & ['something'])(chris & 0.9)"""

    def test_non_strings(self):
        template = "{{#stats}}({{key}} & {{value}}){{/stats}}"
        stats = []
        stats.append({'key': 123, 'value': ['something']})
        stats.append({'key': u"chris", 'value': 0.900})

        ret = pystache.render(template, { 'stats': stats })
        self.assertEquals(ret, self.non_strings_expected)

    def test_unicode(self):
        template = 'Name: {{name}}; Age: {{age}}'
        ret = pystache.render(template, { 'name': u'Henri Poincaré',
            'age': 156 })
        self.assertEquals(ret, u'Name: Henri Poincaré; Age: 156')

    def test_sections(self):
        template = """<ul>{{#users}}<li>{{name}}</li>{{/users}}</ul>"""

        context = { 'users': [ {'name': 'Chris'}, {'name': 'Tom'}, {'name': 'PJ'} ] }
        ret = pystache.render(template, context)
        self.assertEquals(ret, """<ul><li>Chris</li><li>Tom</li><li>PJ</li></ul>""")

    def test_implicit_iterator(self):
        template = """<ul>{{#users}}<li>{{.}}</li>{{/users}}</ul>"""
        context = { 'users': [ 'Chris', 'Tom','PJ' ] }
        ret = pystache.render(template, context)
        self.assertEquals(ret, """<ul><li>Chris</li><li>Tom</li><li>PJ</li></ul>""")

    # The spec says that sections should not alter surrounding whitespace.
    def test_surrounding_whitepace_not_altered(self):
        template = "first{{#spacing}} second {{/spacing}}third"
        ret = pystache.render(template, {"spacing": True})
        self.assertEquals(ret, "first second third")

    def test__section__non_false_value(self):
        """
        Test when a section value is a (non-list) "non-false value".

        From mustache(5):

            When the value [of a section key] is non-false but not a list, it
            will be used as the context for a single rendering of the block.

        """
        template = """{{#person}}Hi {{name}}{{/person}}"""
        context = {"person": {"name": "Jon"}}
        self._assert_rendered("Hi Jon", template, context)

    def test_later_list_section_with_escapable_character(self):
        """
        This is a simple test case intended to cover issue #53.

        The test case failed with markupsafe enabled, as follows:

        AssertionError: Markup(u'foo &lt;') != 'foo <'

        """
        template = """{{#s1}}foo{{/s1}} {{#s2}}<{{/s2}}"""
        context = {'s1': True, 's2': [True]}
        actual = pystache.render(template, context)
        self.assertEquals(actual, """foo <""")


class PystacheWithoutMarkupsafeTests(PystacheTests, unittest.TestCase):

    """Test pystache without markupsafe enabled."""

    def setUp(self):
        self.original_markupsafe = renderer.markupsafe
        renderer.markupsafe = None

    def tearDown(self):
        renderer.markupsafe = self.original_markupsafe


# If markupsafe is available, then run the same tests again but without
# disabling markupsafe.
_BaseClass = unittest.TestCase if renderer.markupsafe else object
class PystacheWithMarkupsafeTests(PystacheTests, _BaseClass):

    """Test pystache with markupsafe enabled."""

    # markupsafe.escape() escapes single quotes: "'" becomes "&#39;".
    non_strings_expected = """(123 & [&#39;something&#39;])(chris & 0.9)"""

    def test_markupsafe_available(self):
        self.assertTrue(renderer.markupsafe, "markupsafe isn't available.  "
            "The with-markupsafe tests shouldn't be running.")
