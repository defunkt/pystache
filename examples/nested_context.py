import pystache

class NestedContext(pystache.View):
    template_path = 'examples'

    def foo(self):
        return {'thing1': 'one', 'thing2': 'foo'}
