import pystache

class Unescaped(pystache.View):
    template_path = 'examples'

    def title(self):
        return "Bear > Shark"
