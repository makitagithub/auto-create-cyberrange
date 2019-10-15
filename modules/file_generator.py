import jinja2
import os

from modules.device_creator import create_devices
from modules.ansible_data_generator import create_network_map, create_host_map, create_network_ips


def _load_template(template_name):
    """ Returns a loaded jinja2 template. """

    template_loader = jinja2.FileSystemLoader(searchpath="templates")
    template_env = jinja2.Environment(loader=template_loader, trim_blocks=True)
    return template_env.get_template(template_name)


def _generate_file(filename, output_string):
    """ Generates a file from output string. """

    try:
        new_file = open(filename, "w")
        new_file.write(output_string)
    except IOError:
        print("Error: cannot write to this location.")


def _create_role_directory(role_name):
    """ Creates directory structure for a role. """

    try:
        os.mkdir("provisioning")
    except FileExistsError:
        pass
    try:
        os.mkdir("provisioning/roles")
    except FileExistsError:
        pass
    try:
        os.mkdir("provisioning/roles/" + role_name)
    except FileExistsError:
        pass
    try:
        os.mkdir("provisioning/roles/" + role_name +"/tasks")
    except FileExistsError:
        pass


def _find_user_ansible_files(definitions):
    """ Finds the user ansible files and returns a list of host names. """
    host_names = []

    for host in definitions["hosts"]:
        if os.path.isfile("provisioning/" + host["name"] + ".yml" ):
            host_names.append(host["name"])

    return host_names

def generate_vagrantfile(definitions):
    """ Writes the prepared output to a Vagrantfile. """
    
    device_definitions = create_devices(definitions)
    user_ansible_files = _find_user_ansible_files(definitions)
    template = _load_template("vagrantfile")
    output = template.render(devices=device_definitions, user_files=user_ansible_files)
    _generate_file("Vagrantfile", output)
    
    print("Info: Vagrantfile successfully created.")


def _generate_playbook(definitions):
    """ Generates the main playbook. """

    host_map = create_host_map(definitions["net_mappings"], definitions["router_mappings"], definitions["hosts"])
    network = create_network_map(
            definitions["net_mappings"], definitions["router_mappings"])
    network_ips = create_network_ips(definitions["networks"])
    
    template = _load_template("playbook")
    output = template.render(hosts=host_map, routers=network, network_ips=network_ips)

    try:
        os.mkdir("provisioning")
    except FileExistsError:
        pass

    _generate_file("./provisioning/playbook.yml", output)


def _generate_device_configuration(definitions):
    """ Generates a playbook with basic device configutarion. """

    host_map = create_host_map(definitions["net_mappings"], definitions["router_mappings"], definitions["hosts"])
    network = create_network_map(
            definitions["net_mappings"], definitions["router_mappings"]) 
    network_ips = create_network_ips(definitions["networks"])

    template = _load_template("device_configuration")
    output = template.render(hosts=host_map, routers=network, network_ips=network_ips)

    try:
        os.mkdir("provisioning")
    except FileExistsError:
        pass

    _generate_file("./provisioning/device_configuration.yml", output)


def _generate_hosts_role(definitions):
    """ Generates hosts role. """

    host_map = create_host_map(definitions["net_mappings"], definitions["router_mappings"], definitions["hosts"])

    network = create_network_map(
            definitions["net_mappings"], definitions["router_mappings"])

    template = _load_template("hosts")
    output = template.render(hosts=host_map, routers=network)

    _create_role_directory("hosts")
    _generate_file("./provisioning/roles/hosts/tasks/main.yml", output)


def _generate_routers_role(definitions):
    """ Generates routers role. """

    if not definitions['routers'] or not definitions['router_mappings']:
        print("Info: No router definition was found. Skipping router creation.")
        return

    host_map = create_host_map(definitions["net_mappings"], definitions["router_mappings"], definitions["hosts"])

    network = create_network_map(
            definitions["net_mappings"], definitions["router_mappings"]) 

    template = _load_template("routers")
    output = template.render(hosts=host_map, routers=network)

    _create_role_directory("routers")
    _generate_file("./provisioning/roles/routers/tasks/main.yml", output)


def generate_ansible_files(device_definitions):
    """ Generates files for ansible. """
    
    _generate_playbook(device_definitions)
    _generate_device_configuration(device_definitions)
    _generate_hosts_role(device_definitions)
    _generate_routers_role(device_definitions)

    print("Info: Ansible files successfully created.")
