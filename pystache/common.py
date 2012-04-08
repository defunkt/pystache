# coding: utf-8

"""
Exposes common functions.

"""

# This function was designed to be portable across Python versions -- both
# with older versions and with Python 3 after applying 2to3.
def read(path):
    """
    Return the contents of a text file as a byte string.

    """
    # Opening in binary mode is necessary for compatibility across Python
    # 2 and 3.  In both Python 2 and 3, open() defaults to opening files in
    # text mode.  However, in Python 2, open() returns file objects whose
    # read() method returns byte strings (strings of type `str` in Python 2),
    # whereas in Python 3, the file object returns unicode strings (strings
    # of type `str` in Python 3).
    f = open(path, 'rb')
    # We avoid use of the with keyword for Python 2.4 support.
    try:
        return f.read()
    finally:
        f.close()
