import pystache

class Inverted(pystache.View):
    template_path = 'examples'

    def t(self):
        return True

    def f(self):
        return False

    def two(self):
        return 'two'
