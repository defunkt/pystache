# encoding: utf-8

import unittest
import pystache

class TestPystache(unittest.TestCase):
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

    def test_non_strings(self):
        template = "{{#stats}}({{key}} & {{value}}){{/stats}}"
        stats = []
        stats.append({'key': 123, 'value': ['something']})
        stats.append({'key': u"chris", 'value': 0.900})

        ret = pystache.render(template, { 'stats': stats })
        self.assertEquals(ret, """(123 & ['something'])(chris & 0.9)""")

    def test_unicode(self):
        template = 'Name: {{name}}; Age: {{age}}'
        ret = pystache.render(template, { 'name': u'Henri Poincaré',
            'age': 156 })
        self.assertEquals(ret, u'Name: Henri Poincaré; Age: 156')

    def test_sections(self):
        template = """
<ul>
  {{#users}}
    <li>{{name}}</li>
  {{/users}}
</ul>
"""

        context = { 'users': [ {'name': 'Chris'}, {'name': 'Tom'}, {'name': 'PJ'} ] }
        ret = pystache.render(template, context)
        self.assertEquals(ret, """
<ul>
  <li>Chris</li><li>Tom</li><li>PJ</li>
</ul>
""")

if __name__ == '__main__':
    unittest.main()
