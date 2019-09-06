import jinja2
import os

from modules.device_creator import create_devices
from modules.ansible_files_generator import create_network_map, create_host_map


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


def generate_vagrantfile(definitions):
    """ Writes the prepared output to a Vagrantfile. """
    
    device_definitions = create_devices(definitions)
    template = _load_template("base")
    output = template.render(devices=device_definitions)
    _generate_file("Vagrantfile", output)
    
    print("Info: Vagrantfile successfully created.")


def _generate_routers_playbook(definitions):
    """ Generates ansible playbook for router configuration. """
    
    if not definitions['routers'] or not definitions['router_mappings']:
        print("Info: No router definition was found. Skipping router creation.")
        return

    network = create_network_map(
            definitions["net_mappings"], definitions["router_mappings"]) 

    template = _load_template("router")
    output = template.render(network=network)

    try:
        os.mkdir("provision")
    except FileExistsError:
        pass

    _generate_file("./provision/routers_playbook.yaml", output)

    print("Info: Routers successfully created.")


def _generate_host_playbook(definitions): 
    """ Generates ansible playbook for host configuration. """

    host_map = create_host_map(definitions["net_mappings"], definitions["router_mappings"])

    template = _load_template("host")
    output = template.render(hosts=host_map)

    try:
        os.mkdir("provision")
    except FileExistsError:
        pass

    _generate_file("./provision/hosts_playbook.yaml", output)

    print("Info: Hosts successfully created.")


def generate_ansible_files(device_definitions):
    """ Generates files for ansible. """
    _generate_routers_playbook(device_definitions)
    _generate_host_playbook(device_definitions)
