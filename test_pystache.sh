#!/bin/bash
#
# This wrapper script is useful for running tests with different
# PYTHONHASHSEED values.
# 
# Sample usage:
#
#     $ ./test_pystache.sh [ARGS]
#
export PYTHONHASHSEED=$RANDOM
python test_pystache.py "$@"
