import pystache

class Comments(pystache.View):
    template_path = 'examples'

    def title(self):
        return "A Comedy of Errors"
