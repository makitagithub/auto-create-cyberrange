""" This module contains functions for preprocessing. They are supposed to be
called after validating the input but before device creation.
"""

from modules.border_router import create_border_router
from modules.file_manager import open_yaml

FLAVORS = open_yaml("conf/flavors.yml")
ROUTER_ATTRIBUTES = open_yaml("conf/router_attributes.yml")


def _configure_routers(definitions):
    """ Adds predefined parameters to all routers if they are not defined in
    the source yaml.
    """

    for router in definitions["routers"]:
        for parameter, value in ROUTER_ATTRIBUTES.items():
            if parameter not in router:
                router[parameter] = value


def _add_flavors(definitions): 
    """ Changes flavor attribute to cpus and memory. """

    for host in definitions["hosts"]:
        if "flavor" in host:
            if host["flavor"] not in FLAVORS:
                print("Error: Not supported flavor: " + host["flavor"])
                raise AttributeError
            if "memory" not in host:
                host["memory"] = FLAVORS[host["flavor"]]["memory"]
            if "cpus" not in host:
                host["memory"] = FLAVORS[host["flavor"]]["cores"]
            host.pop("flavor")


def preprocess(definitions, flags):
    """
    This function handles the preprocessing, operations that need to be done
    before the actual device creation.

    :param definitions: device definition structure
    :param flags: a structure with command line flags
    """

    try:
        if "border_router" in flags and flags["border_router"]:
            create_border_router(definitions)
    except Exception:
        print("Could not create border router.")
        raise

    try:
        _configure_routers(definitions)
    except Exception:
        print("Could not add router configurations to definitions.")
        raise

    try:
        _add_flavors(definitions)
    except Exception:
        print("Could not add flavor.")
        raise
