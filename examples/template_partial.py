import pystache

class TemplatePartial(pystache.View):
    template_path = 'examples'

    def title(self):
        return "Welcome"

    def title_bars(self):
        return '-' * len(self.title())

    def looping(self):
        return [{'item': 'one'}, {'item': 'two'}, {'item': 'three'}]

    def thing(self):
        return self.get('prop')