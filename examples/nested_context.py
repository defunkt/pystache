import pystache

class NestedContext(pystache.View):
    template_path = 'examples'

    def outer_thing(self):
        return "two"

    def foo(self):
        return {'thing1': 'one', 'thing2': 'foo'}

    def derp(self):
        return [{'inner': 'car'}]
        
    def herp(self):
        return [{'outer': 'car'}]
        
    def nested_context_in_view(self):
        return 'it works!' if self.get('outer') == self.get('inner') else ''