import pystache

class RepeatingSections(pystache.View):
    template_path = 'examples'

    def r1(self):
        return [True, True]

    def r2(self):
        return [True, True, True]
