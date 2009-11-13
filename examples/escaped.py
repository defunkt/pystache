import pystache

class Escaped(pystache.View):
    template_path = 'examples'

    def title(self):
        return "Bear > Shark"
