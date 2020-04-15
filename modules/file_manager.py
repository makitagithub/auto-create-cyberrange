""" This module handles file imports and creations in general. """

import os
import shutil
import sys

import jinja2
import yaml

OUTPUT_DIRECTORY = "sandbox"


def open_yaml(file_name):
    """ Opens and returns a file from the argument. """

    try:
        with open(str(file_name)) as input_file:
            return yaml.safe_load(input_file)
    except yaml.YAMLError:
        cleanup_and_exit("Could not parse yaml file " + str(file_name) + ".")
    except IOError:
        cleanup_and_exit("Could not open yaml file " + str(file_name) + ".")


def copy_template_file(template, destination):
    """ Copies playbook templates that does not need jinja or yaml to the
    destination.
    """

    try:
        shutil.copyfile("templates/" + template, "sandbox/" + destination)
    except IOError:
        cleanup_and_exit("Could not copy template file " + str(file_name) + ".")


def dump_to_yaml(data, filename):
    """ Writes a data structure to a YAML document.

    :param data: a dict or list which should be written to file
    :param filename: name of the target file
    """

    file_path = OUTPUT_DIRECTORY + "/" + str(filename)

    try:
        with open(file_path, 'w') as stream:
            yaml.dump(data, stream)
    except IOError:
        cleanup_and_exit("Could not create yaml file " + file_path + ".")


def generate_file(template, filename, **template_args):
    """ Generates a file using a template.
    
    :param template: name of the template file
    :param filename: path to the output file inside the output directory
    :param template_args: arbitrary number of named args for the template
    """

    inventory_template = _load_template(template)
    output = inventory_template.render(**template_args)
    _write_to_file(filename, output)


def _write_to_file(filename, output_string):
    """ Generates a file from output string. """

    try:
        new_file = open(OUTPUT_DIRECTORY + "/" + filename, "w")
        new_file.write(output_string)
    except IOError:
        cleanup_and_exit("Could not create file " + str(filename) + ".")


def _load_template(template_name):
    """ Returns a loaded jinja2 template. """

    try:
        template_loader = jinja2.FileSystemLoader(searchpath="templates")
        template_env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
        return template_env.get_template(template_name)
    except jinja2.TemplateNotFound:
        cleanup_and_exit("Could not find template " + str(template_name) + ".")


def _copy_directory(source, destination):
    """ Copies directory recursively form templates directory to the
    destination.
    """

    try:
        shutil.copytree("./templates/" + source, destination)
    except OSError:
        cleanup_and_exit("Could not copy directory " + str(source) + ".")


def _create_provisioning_directories(directory, device_definitions):
    """ Creates all subdirectories for privisioning. """

    try:
        os.mkdir(OUTPUT_DIRECTORY + "/" + directory)
        os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles")

        if device_definitions["hosts"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/hosts")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/hosts/tasks")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/hosts/vars")
        for host in device_definitions["hosts"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + host["name"])
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + host["name"] + "/tasks")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + host["name"] + "/vars")

        if device_definitions["routers"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/routers")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/routers/tasks")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/routers/vars")
        for router in device_definitions["routers"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + router["name"])
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + router["name"] + "/tasks")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + router["name"] + "/vars")

    except FileExistsError:
        pass
    except IOError:
        cleanup_and_exit("Could not create directories for provisioning.")


def prepare_directories(device_definitions):
    """ Prepares the necessary directory structure. """

    shutil.rmtree(OUTPUT_DIRECTORY, True)
    
    try:
        os.mkdir(OUTPUT_DIRECTORY)
    except IOError:
        cleanup_and_exit("Could not create directory ./" + OUTPUT_DIRECTORY + ".")

    _create_provisioning_directories("base_provisioning", device_definitions)
    _create_provisioning_directories("provisioning", device_definitions)

    _copy_directory("interface", OUTPUT_DIRECTORY + "/base_provisioning/roles/interface")
    _copy_directory("common", OUTPUT_DIRECTORY + "/base_provisioning/roles/common")


def cleanup_and_exit(error):
    """ A cleanup function that is called in case of an error. """

    # TODO cleanup

    print("Sandbox creation was NOT successful:")
    print("Error: ", error)

    sys.exit(1)
