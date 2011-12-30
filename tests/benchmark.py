#!/usr/bin/env python
# coding: utf-8

"""
A rudimentary backward- and forward-compatible script to benchmark pystache.

Usage:

tests/benchmark.py 10000

"""

import sys
from timeit import Timer

import pystache

# TODO: make the example realistic.

examples = [
    # Test case: 1
    ("""\
{{#person}}Hi {{name}}{{/person}}""",
    {"person": {"name": "Jon"}},
    "Hi Jon"),
]


def make_test_function(example):

    template, context, expected = example

    def test():
        actual = pystache.render(template, context)
        if actual != expected:
            raise Exception("Benchmark mismatch")

    return test


def main(sys_argv):
    args = sys_argv[1:]
    count = int(args[0])

    print "Benchmarking: %sx" % count
    print

    for example in examples:

        test = make_test_function(example)

        t = Timer(test,)
        print min(t.repeat(repeat=3, number=count))

    print "Done"


if __name__ == '__main__':
    main(sys.argv)

