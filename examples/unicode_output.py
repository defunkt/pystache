# encoding: utf-8

import pystache

class UnicodeOutput(pystache.View):
    template_path = 'examples'

    def name(self):
        try:
            return 'Henri Poincaré'.decode('utf-8')
        except AttributeError:
            return 'Henri Poincaré'
