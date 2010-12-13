import pystache
from examples.lambdas import rot

class PartialsWithLambdas(pystache.View):
    template_path = 'examples'
    
    def rot(self):
        return rot