# coding: utf-8

"""
Exposes a get_doctests() function for the project's test harness.

"""

from lib2to3.main import main as lib2to3main
import doctest
import os
import pkgutil
from shutil import copyfile
import sys
import traceback

from pystache.tests.common import PACKAGE_DIR, TEXT_DOCTEST_PATHS


# This module follows the guidance documented here:
#
#   http://docs.python.org/library/doctest.html#unittest-api
#

def get_doctests(text_file_dir):
    """
    Return a list of TestSuite instances for all doctests in the project.

    Arguments:

      text_file_dir: the directory in which to search for all text files
        (i.e. non-module files) containing doctests.

    """
    # Since module_relative is False in our calls to DocFileSuite below,
    # paths should be OS-specific.  See the following for more info--
    #
    #   http://docs.python.org/library/doctest.html#doctest.DocFileSuite
    #
    paths = [os.path.normpath(os.path.join(text_file_dir, path)) for path in TEXT_DOCTEST_PATHS]

    py_version = sys.version_info
    if py_version >= (3,):
        paths = _convert_paths(paths)

    suites = []

    for path in paths:
        suite = doctest.DocFileSuite(path, module_relative=False)
        suites.append(suite)

    modules = _get_module_doctests(PACKAGE_DIR)
    for module in modules:
        suite = doctest.DocTestSuite(module)
        suites.append(suite)

    return suites


def _convert_2to3(path):
    """
    Convert the given file, and return the path to the converted files.

    """
    base, ext = os.path.splitext(path)
    # For example, "README.temp2to3.rst".
    new_path = "%s.temp2to3%s" % (base, ext)

    copyfile(path, new_path)

    args = ['--doctests_only', '--no-diffs', '--write', '--nobackups', new_path]
    lib2to3main("lib2to3.fixes", args=args)

    return new_path


def _convert_paths(paths):
    """
    Convert the given files, and return the paths to the converted files.

    """
    new_paths = []
    for path in paths:
        new_path = _convert_2to3(path)
        new_paths.append(new_path)

    return new_paths


def _get_module_doctests(package_dir):
    modules = []

    for pkg in pkgutil.walk_packages([package_dir]):
        # The importer is a pkgutil.ImpImporter instance:
        #
        #   http://docs.python.org/library/pkgutil.html#pkgutil.ImpImporter
        #
        importer, module_name, is_package = pkg
        if is_package:
            # Otherwise, we will get the following error when adding tests:
            #
            #   ValueError: (<module 'tests' from '.../pystache/tests/__init__.pyc'>, 'has no tests')
            #
            continue
        # The loader is a pkgutil.ImpLoader instance.
        loader = importer.find_module(module_name)
        try:
            module = loader.load_module(module_name)
        except ImportError, e:
            # In some situations, the test harness was swallowing and/or
            # suppressing the display of the stack trace when errors
            # occurred here.  The following code makes errors occurring here
            # easier to troubleshoot.
            details = "".join(traceback.format_exception(*sys.exc_info()))
            raise ImportError(details)
        modules.append(module)

    return modules
