import pystache

class Inverted(pystache.View):
    template_path = 'examples'

    def t(self):
        return True

    def f(self):
        return False

    def two(self):
        return 'two'

class InvertedLists(Inverted):
    template_name = 'inverted'

    def t(self):
        return [0, 1, 2]

    def f(self):
        return []
