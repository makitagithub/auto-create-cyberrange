""" This module generates a Vagrantfile from input device definitions. """

import jinja2

from modules.file_manager import load_template, generate_file, open_yaml

VAGRANT_MAPPING = open_yaml("conf/vagrant_mapping.yml")
VIRTUALBOX_MAPPING = open_yaml("conf/virtualbox_mapping.yml")


def _create_simple_attribute(key, value, attribute_type):
    """ Creates simple vagrant attributes like string, integer or boolean. """

    attribute = dict()
    attribute["type"] = attribute_type
    attribute["command"] = key
    attribute["value"] = value

    return attribute


def _create_commands(device_attributes, device_type, input_definitions, flags):
    """ This function creates basic vagrant definition commands for a device. """

    commands = []
    vb_commands = []

    for attribute, value in device_attributes.items():
        if attribute in VAGRANT_MAPPING["string"]:
            commands.append(_create_simple_attribute(VAGRANT_MAPPING["string"][attribute], value, "string"))
        elif attribute in VAGRANT_MAPPING["boolean"]:
            commands.append(_create_simple_attribute(VAGRANT_MAPPING["boolean"][attribute], value, "boolean"))
        elif attribute in VAGRANT_MAPPING["integer"]:
            commands.append(_create_simple_attribute(VAGRANT_MAPPING["integer"][attribute], value, "integer"))
        elif attribute in VIRTUALBOX_MAPPING["integer"]:
            vb_commands.append(_create_simple_attribute(VIRTUALBOX_MAPPING["integer"][attribute], value, "integer"))

    if vb_commands:
        vb = dict()
        vb["type"] = "provider"
        vb["name"] = "virtualbox"
        vb["commands"] = vb_commands
        commands.append(vb)
    
    return commands


def _create_ansible_commands(playbook_location, flags):
    """ Creates commands for running a playbook from the Vagrantfile. """

    commands = []
    
    playbook = dict()
    playbook["type"] = "string"
    playbook["command"] = "playbook"
    playbook["value"] = playbook_location
    commands.append(playbook)

    if "verbose_ansible" in flags and flags["verbose_ansible"]:
        verbosity = dict()
        verbosity["type"] = "boolean"
        verbosity["command"] = "verbose"
        verbosity["value"] = True
        commands.append(verbosity)

    return commands


def _find_netmask(network_name, networks):
    """ Returns the netmask of a network address from network name. """

    for network in networks:
        if network['name'] == network_name:
            address, netmask = network['cidr'].split('/')
            return netmask


def _add_networks_to_device(definition, mappings, input_definitions):
    """ Adds networks to the vagrant definition of one device. """

    for mapping in mappings:
        if mapping[definition["type"]] == definition["name"]:
            network = dict()
            network["type"] = "network"
            network["network_type"] = "private_network"
            network["name"] = mapping["network"]
            network["ip"] = mapping["ip"]
            network["netmask"] = _find_netmask(mapping["network"], input_definitions["networks"])
            definition["commands"].append(network)


def _add_all_networks(vagrant_definitions, input_definitions, flags):
    """ Adds all networks to vagrant definitions. """

    for definition in vagrant_definitions:
        if definition["type"] == "host":
            _add_networks_to_device(definition, input_definitions["net_mappings"], input_definitions)      
        elif definition["type"] == "router":
            _add_networks_to_device(definition, input_definitions["router_mappings"], input_definitions)


def _call_provisioner(flags):
    """ Creates entry to vagrant definitions for calling the provisioner. """
    
    provisioner_calls = []

    config_playbook = dict()
    config_playbook["type"] = "provision"
    if "ansible_local" in flags and flags["ansible_local"]:
        config_playbook["provisioner"] = "ansible_local"
    else:
        config_playbook["provisioner"] = "ansible"
    config_playbook["note"] = "basic configuration of devices and networks"
    config_playbook["commands"] = _create_ansible_commands(
            "base_provisioning/device_configuration.yml", flags)

    provisioner_calls.append(config_playbook)

    user_playbook = dict()
    user_playbook["type"] = "provision"
    if "ansible_local" in flags and flags["ansible_local"]:
        user_playbook["provisioner"] = "ansible_local"
    else:
        user_playbook["provisioner"] = "ansible"
    user_playbook["note"] = "user configuration of devices"
    user_playbook["commands"] = _create_ansible_commands(
            "base_provisioning/playbook.yml", flags)
    
    provisioner_calls.append(user_playbook)

    return provisioner_calls


def _build_vagrant_definitions(input_definitions, flags):
    """
    Creates a definition structure that is more suitable for Vagrantfile
    generation than input definitions.
    """

    vagrant_definitions = []
    for router in input_definitions["routers"]:
        device = dict()
        device["type"] = "router"
        device["name"] = router["name"]
        device["commands"] = _create_commands(router, "router", input_definitions, flags)
        vagrant_definitions.append(device)

    for host in input_definitions["hosts"]:
        device = dict()
        device["type"] = "host"
        device["name"] = host["name"]
        device["commands"] = _create_commands(host, "host", input_definitions, flags)
        vagrant_definitions.append(device)

    _add_all_networks(vagrant_definitions, input_definitions, flags)
    
    vagrant_definitions.extend(_call_provisioner(flags))
    
    return vagrant_definitions


def _build_vagrantfile(vagrant_definitions):
    """
    Generates the Vagrantfile using the vagrantfile template and vagrant
    definitions.
    """

# TODO change newvagrantfile to vagrantfile 
    template = load_template("newvagrantfile")
    output = template.render(defs=vagrant_definitions)
    generate_file("Vagrantfile", output)
    

def generate_vagrantfile(input_definitions, flags):
    """
    This method is responsible for Vagrantfile generation.

    :param input_definitions: device definitions from the input file
    :param flags: command line flags
    """

    try:
        vagrant_definitions = _build_vagrant_definitions(input_definitions, flags)
    except Exception:
       print("Could not create definitions for Vagrantfile.")
       raise

    try:
       _build_vagrantfile(vagrant_definitions)
    except Exception:
       print("Could not generate Vagrantfile.")
       raise
