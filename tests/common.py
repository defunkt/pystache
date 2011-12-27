# coding: utf-8

"""
Provides test-related code that can be used by all tests.

"""

import os


DATA_DIR = 'tests/data'

def get_data_path(file_name):
    return os.path.join(DATA_DIR, file_name)

