"""Contains functions for generating a Vagrantfile from input definitions."""

from modules.file_manager import generate_file, open_yaml

VAGRANT_MAPPING = open_yaml("conf/vagrant_mapping.yml")
VIRTUALBOX_MAPPING = open_yaml("conf/virtualbox_mapping.yml")
BOX_MAPPING = open_yaml("conf/box_mapping.yml")
BASE_PLAYBOOK = "base_provisioning/device_configuration.yml"
USER_PLAYBOOK = "provisioning/playbook.yml"


def _create_simple_attribute(key, value, attribute_type):
    """Create simple vagrant attributes like string, integer or boolean."""
    attribute = dict()
    attribute["type"] = attribute_type
    attribute["command"] = key
    attribute["value"] = value

    return attribute


def _create_complex_attribute(key, value):
    """Create complex vagrant attributes that are not string, int or bool."""
    separators = {VAGRANT_MAPPING["other"]["synced_folder"]: ""}

    attribute = dict()
    attribute["type"] = "other"
    attribute["command"] = key
    attribute["separator"] = separators[key]
    attribute["value"] = value

    return attribute


def _create_special_commands(attribute, value):
    """Create special commands that cannot be mapped to a single command."""
    special_attributes = []
    if attribute == "base_box":
        if "image" in value:
            if value["image"] in BOX_MAPPING:
                value["image"] = BOX_MAPPING[value["image"]]
            box_name = dict()
            box_name["type"] = "string"
            box_name["command"] = "vm.box"
            box_name["value"] = value["image"]
            special_attributes.append(box_name)
        if "man_user" in value:
            user = dict()
            user["type"] = "string"
            user["command"] = "ssh.username"
            user["value"] = value["man_user"]
            special_attributes.append(user)

    return special_attributes


def _create_commands(device_attributes):
    """Create basic vagrant definition commands for a device."""
    commands = []
    vb_commands = []

    for attribute, value in device_attributes.items():
        if attribute in VAGRANT_MAPPING["string"]:
            vagrant_attribute = VAGRANT_MAPPING["string"][attribute]
            commands.append(_create_simple_attribute(vagrant_attribute, value,
                                                     "string"))
        elif attribute in VAGRANT_MAPPING["boolean"]:
            vagrant_attribute = VAGRANT_MAPPING["boolean"][attribute]
            commands.append(_create_simple_attribute(vagrant_attribute, value,
                                                     "boolean"))
        elif attribute in VAGRANT_MAPPING["integer"]:
            vagrant_attribute = VAGRANT_MAPPING["integer"][attribute]
            commands.append(_create_simple_attribute(vagrant_attribute, value,
                                                     "integer"))
        elif attribute in VAGRANT_MAPPING["other"]:
            vagrant_attribute = VAGRANT_MAPPING["other"][attribute]
            commands.append(_create_complex_attribute(vagrant_attribute,
                                                      value))
        elif attribute in VAGRANT_MAPPING["special"]:
            commands.extend(_create_special_commands(attribute, value))
        elif attribute in VIRTUALBOX_MAPPING["integer"]:
            vagrant_attribute = VIRTUALBOX_MAPPING["integer"][attribute]
            vb_commands.append(_create_simple_attribute(vagrant_attribute,
                                                        value, "integer"))

    if vb_commands:
        virtual_box_command = dict()
        virtual_box_command["type"] = "provider"
        virtual_box_command["name"] = "virtualbox"
        virtual_box_command["commands"] = vb_commands
        commands.append(virtual_box_command)

    return commands


def _create_ansible_commands(playbook_location, input_definitions, flags):
    """Create commands for running a playbook from the Vagrantfile."""
    commands = []

    playbook = dict()
    playbook["type"] = "string"
    playbook["command"] = "playbook"
    playbook["value"] = playbook_location
    commands.append(playbook)

    if "verbose_ansible" in flags and flags["verbose_ansible"]:
        verbosity = dict()
        verbosity["type"] = "string"
        verbosity["command"] = "verbose"
        verbosity["value"] = "vv"
        commands.append(verbosity)

    groups = dict()
    groups["type"] = "groups"
    groups["groups"] = dict()
    host_names = []
    for host in input_definitions["hosts"]:
        host_names.append(host["name"])
    groups["groups"]["hosts"] = host_names
    router_names = []
    for router in input_definitions["routers"]:
        router_names.append(router["name"])
    groups["groups"]["routers"] = router_names
    if "groups" in input_definitions:
        for group in input_definitions["groups"]:
            groups["groups"][group["name"]] = group["nodes"]
    commands.append(groups)

    if "ansible_local" in flags and flags["ansible_local"]:
        install_mode = dict()
        install_mode["type"] = "string"
        install_mode["command"] = "install_mode"
        install_mode["value"] = "pip"
        commands.append(install_mode)

    extravars = dict()
    extravars["type"] = "dictionary"
    extravars["command"] = "extra_vars"
    extravars["dictionary"] = dict()
    extravars["dictionary"]["ansible_python_interpreter"] = \
        "\"/usr/bin/python3\""
    if "extra_vars" in flags and flags["extra_vars"]:
        user_extra_vars = open_yaml(flags["extra_vars"])
        extravars["dictionary"].update(user_extra_vars)
    commands.append(extravars)

    return commands


def _find_netmask(network_name, networks):
    """Return the netmask of a network address from network name."""
    for network in networks:
        if network['name'] == network_name:
            address, netmask = network['cidr'].split('/')
            return netmask
    return None


def _add_networks_to_device(definition, mappings, input_definitions):
    """Add networks to the vagrant definition of one device."""
    for mapping in mappings:
        if mapping[definition["type"]] == definition["name"]:
            network = dict()
            network["type"] = "network"
            network["network_type"] = "private_network"
            network["name"] = mapping["network"]
            network["ip"] = mapping["ip"]
            network["netmask"] = _find_netmask(mapping["network"],
                                               input_definitions["networks"])
            definition["commands"].append(network)


def _add_all_networks(vagrant_definitions, input_definitions, flags):
    """Add all networks to vagrant definitions."""
    for definition in vagrant_definitions:
        if definition["type"] == "host":
            _add_networks_to_device(definition,
                                    input_definitions["net_mappings"],
                                    input_definitions)
        elif definition["type"] == "router":
            _add_networks_to_device(definition,
                                    input_definitions["router_mappings"],
                                    input_definitions)


def _call_provisioner(input_definitions, flags):
    """Create entry to vagrant definitions for calling the provisioner."""
    provisioner_calls = []

    config_playbook = dict()
    config_playbook["type"] = "provision"
    if "ansible_local" in flags and flags["ansible_local"]:
        config_playbook["provisioner"] = "ansible_local"
    else:
        config_playbook["provisioner"] = "ansible"
    config_playbook["note"] = "basic configuration of devices and networks"
    config_playbook["commands"] = _create_ansible_commands(BASE_PLAYBOOK,
                                                           input_definitions,
                                                           flags)

    provisioner_calls.append(config_playbook)

    user_playbook = dict()
    user_playbook["type"] = "provision"
    if "ansible_local" in flags and flags["ansible_local"]:
        user_playbook["provisioner"] = "ansible_local"
    else:
        user_playbook["provisioner"] = "ansible"
    user_playbook["note"] = "user configuration of devices"
    user_playbook["commands"] = _create_ansible_commands(USER_PLAYBOOK,
                                                         input_definitions,
                                                         flags)

    provisioner_calls.append(user_playbook)

    return provisioner_calls


def _build_vagrant_definitions(input_definitions, flags):
    """Create a definition structure for vagrant.

    This structure is more suitable for Vagrantfile generation than input
    definitions.
    """
    vagrant_definitions = []
    for router in input_definitions["routers"]:
        device = dict()
        device["type"] = "router"
        device["name"] = router["name"]
        device["commands"] = _create_commands(router)
        vagrant_definitions.append(device)

    for host in input_definitions["hosts"]:
        device = dict()
        device["type"] = "host"
        device["name"] = host["name"]
        device["commands"] = _create_commands(host)
        vagrant_definitions.append(device)

    _add_all_networks(vagrant_definitions, input_definitions, flags)

    vagrant_definitions.extend(_call_provisioner(input_definitions, flags))

    return vagrant_definitions


def generate_vagrantfile(input_definitions, flags):
    """Generate the Vagrantfile.

    :param input_definitions: device definitions from the input file
    :param flags: command line flags
    """
    vagrant_definitions = _build_vagrant_definitions(input_definitions, flags)

    generate_file("vagrantfile", "Vagrantfile", defs=vagrant_definitions)
