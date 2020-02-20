""" This module contains functions for preprocessing. They are supposed to be
called after validating the input but before device creation.
"""

from modules.routing import create_border_router

def preprocess(definitions, flags):
    """
    This function handles the preprocessing, operations that need to be done
    before the actual device creation.

    :param definitions: device definition structure
    :param flags: a structure with command line flags
    """

    """ Creating Border router """
    create_border_router(definitions)
