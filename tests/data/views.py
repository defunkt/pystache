# coding: utf-8

from pystache.view import View

class SayHello(object):

    def to(self):
        return "World"


class SampleView(View):
    pass


class NonAscii(View):
    pass
