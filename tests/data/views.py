# coding: utf-8

from pystache import CustomizedTemplate

class SayHello(object):

    def to(self):
        return "World"


class SampleView(CustomizedTemplate):
    pass


class NonAscii(CustomizedTemplate):
    pass
