import pystache

class UnicodeInput(pystache.View):
    template_path = 'examples'
    template_encoding = 'utf8'

    def age(self):
        return 156
