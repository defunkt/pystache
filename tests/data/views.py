# coding: utf-8

from pystache import TemplateSpec

class SayHello(object):

    def to(self):
        return "World"


class SampleView(TemplateSpec):
    pass


class NonAscii(TemplateSpec):
    pass
