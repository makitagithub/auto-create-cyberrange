"""Contains functions for controller creation."""


from netaddr import *
from itertools import chain

CONTROLLER_NAME = "controller"
CONTROLLER_BOX_NAME = "debian/contrib-stretch64"
CONTROLLER_MEMORY = 512


def _are_controller_parameters_free(definitions):
    """Check if controller parameters are not already taken."""
    for host in definitions["hosts"]:
        if host["name"] == CONTROLLER_NAME:
            return False
        # TODO add other parameters

    return True


def _is_ip_available(ip, definitions):
    """Check if the given ip is used somewhere"""
    for mapping in chain(definitions["router_mappings"],
                         definitions["net_mappings"]):
        if mapping["ip"] == ip:
            return False
    return True


def _find_available_ip(definitions):
    """Return an available ip for the controller"""
    network = IPNetwork(definitions["networks"][0]["cidr"])
    for ip in network:
        if _is_ip_available(ip, definitions):
            return str(ip)


def _add_controller(definitions):
    """Add controller to definitions"""
    controller_ip = _find_available_ip(definitions)
    controller = dict()
    controller["name"] = CONTROLLER_NAME
    controller["base_box"] = dict()
    controller["base_box"]["image"] = CONTROLLER_BOX_NAME
    controller["memory"] = CONTROLLER_MEMORY
    definitions["hosts"].append(controller)
    mapping = dict()
    mapping["host"] = CONTROLLER_NAME
    mapping["network"] = definitions["networks"][0]["name"]
    mapping["ip"] = controller_ip
    definitions["net_mappings"].append(mapping)


def create_controller(definitions):
    """Add the definition of controller to definitions.

    :param definitions: device definition structure
    """

    # TODO this should be later moved to input check
    if not _are_controller_parameters_free(definitions):
        raise ValueError("A device with the same name as border router "
                         "already exists.")

    _add_controller(definitions)
