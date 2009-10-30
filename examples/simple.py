import pystache

class Simple(pystache.View):
    template_path = 'examples'

    def thing(self):
        return "pizza"
