"""This module contains functions for preprocessing.

They are supposed to be called after validating the input but before device
creation.
"""

import itertools

from modules.border_router import create_border_router
from modules.controller import create_controller
from modules.file_manager import open_yaml, cleanup_and_exit

FLAVORS = open_yaml("conf/flavors.yml")
ROUTER_ATTRIBUTES = open_yaml("conf/router_attributes.yml")
DUMMY_ROUTER_NAME = "dummy-router"


def _add_missing_tags(definitions):
    """Add necessary structures to the input if they are missing."""
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
    """Add predefined parameters to all routers.

    Adds them if they are not defined in the source yaml.
    """
    for router in definitions["routers"]:
        for parameter, value in ROUTER_ATTRIBUTES.items():
            if parameter not in router:
                router[parameter] = value


def _add_extra_arguments(definitions, flags):
    """Add extra arguments to definitions if they are not present."""
    if "border_router" in flags and flags["ansible_local"]:
        for device in itertools.chain(definitions["hosts"],
                                      definitions["routers"]):
            if "synced_folder" not in device and "communicator" not in device:
                device["synced_folder"] = "\".\", \"/vagrant\", type: \"rsync"\
                                          "\", rsync__exclude: \".git/\""


def _add_flavors(definitions):
    """Change flavor attribute to cpus and memory."""
    for host in definitions["hosts"]:
        if "flavor" in host and host["flavor"]:
            if host["flavor"] not in FLAVORS:
                print("Error: Not supported flavor: " + host["flavor"])
                raise AttributeError
            if "memory" not in host:
                host["memory"] = FLAVORS[host["flavor"]]["memory"]
            if "cpus" not in host:
                host["cpus"] = FLAVORS[host["flavor"]]["cores"]
            host.pop("flavor")


def _delete_dummy_router(definitions):
    """Delete dummy router if it is defined."""
    for router in definitions["routers"]:
        if router["name"] == DUMMY_ROUTER_NAME:
            definitions["routers"].remove(router)
            return


def _add_usb_passthrough(definitions):
    """Add usb passthrough to devices"""
    for host in definitions["hosts"]:
        if "extra" in host and host["extra"]:
            if "usb_passthrough" in host["extra"]:
                host["vb_customize"] = '["modifyvm", :id, "--usb", "on"]'


def _find_windows_boxes(definitions):
    """Find and return list of host names with windows boxes."""
    windows_hosts = []
    for host in definitions["hosts"]:
        if "windows" in host["base_box"]["image"].lower():
            windows_hosts.append(host["name"])
    return windows_hosts


def _add_windows_attributes(host):
    """Add vagrant attributes to windows hosts"""
    host["communicator"] = "winrm"
    host["winrm_username"] = "windows"
    host["winrm_password"] = "vagrant"


def preprocess(definitions, flags):
    """Run preprocessing.

    Handles perations that need to be done before the actual device creation.
    :param definitions: device definition structure
    :param flags: a structure with command line flags
    """
    try:
        _add_missing_tags(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not add missing tags.")

    try:
        _delete_dummy_router(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not delete dummy router.")

    try:
        if "border_router" in flags and flags["border_router"]:
            create_border_router(definitions)
    except (ValueError, IndexError) as error:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not create border router (" + error + ")")

    windows_hosts = _find_windows_boxes(definitions)
    try:
        if windows_hosts:
            create_controller(definitions)
    except (ValueError, IndexError) as error:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not create controller (" + error + ")")

    try:
        for host in definitions["hosts"]:
            if host["name"] in windows_hosts:
                _add_windows_attributes(host)
    except (ValueError, IndexError) as error:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not create controller (" + error + ")")

    try:
        _configure_routers(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not add router configurations to definitions.")

    try:
        _add_extra_arguments(definitions, flags)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not add extra arguments to definitions.")

    try:
        _add_flavors(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not add flavors.")

    try:
        _add_usb_passthrough(definitions)
    except Exception:
        cleanup_and_exit("Preprocessing not successful: "
                         "Could not add USB passthrough.")
