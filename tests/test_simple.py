import unittest
import pystache

class TestSimple(unittest.TestCase):
    
    def test_simple_render(self):
        tmpl = '{{derp}}'
        
        self.assertEqual('herp', pystache.Template(tmpl, {'derp': 'herp'}).render())