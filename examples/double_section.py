import pystache

class DoubleSection(pystache.View):
    template_path = 'examples'

    def t(self):
        return True

    def two(self):
        return "second"
