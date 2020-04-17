""" This module contains functions for preprocessing. They are supposed to be
called after validating the input but before device creation.
"""

from modules.border_router import create_border_router
from modules.file_manager import open_yaml

FLAVORS = open_yaml("conf/flavors.yml")
ROUTER_ATTRIBUTES = open_yaml("conf/router_attributes.yml")

def _add_missing_tags(definitions):
    """ Adds necessary structures to the input if they are missing. """

    if "routers" not in definitions:
        definitions["routers"] = []
    if "router_mappings" not in definitions:
        definitions["router_mappings"] = []
    if "hosts" not in definitions:
        definitions["hosts"] = []
    if "net_mappings" not in definitions:
        definitions["net_mappings"] = []
    if "networks" not in definitions:
        definitions["networks"] = []


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
                host["cpus"] = FLAVORS[host["flavor"]]["cores"]
            host.pop("flavor")


def preprocess(definitions, flags):
    """
    This function handles the preprocessing, operations that need to be done
    before the actual device creation.

    :param definitions: device definition structure
    :param flags: a structure with command line flags
    """

    try:
        _add_missing_tags(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: Could not add missing tags.")

    try:
        if "border_router" in flags and flags["border_router"]:
            create_border_router(definitions)
    except (ValueError, IndexError) as e:
        cleanup_and_exit("Preprocessing not successful: Could not create border router (" + e + ")")

    try:
        _configure_routers(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: Could not add router configurations to definitions.")

    try:
        _add_flavors(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: Could not add flavors.")
