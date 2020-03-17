""" This module handles file imports and creations in general. """

import jinja2
import os
import shutil
import yaml

OUTPUT_DIRECTORY = "sandbox"


def open_yaml(file_name):
    """ Opens and returns a file from the argument. """
    try:
        input_file = open(str(file_name))
        return yaml.safe_load(input_file)
    except IOError:
        print("Error: Cannot open the required file: " + str(file_name))
        raise
    finally:
        input_file.close()


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
        print("Error: cannot write to this location.")
        raise


def _load_template(template_name):
    """ Returns a loaded jinja2 template. """

    template_loader = jinja2.FileSystemLoader(searchpath="templates")
    template_env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    return template_env.get_template(template_name)

def _create_provisioning_directories(directory, device_definitions):
    """ Creates all subdirectories for privisioning. """

    try:
        os.mkdir(OUTPUT_DIRECTORY + "/" + directory)
        os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles")

        if device_definitions["hosts"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/hosts")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/hosts/tasks")
        for host in device_definitions["hosts"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + host["name"])
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + host["name"] + "/tasks")

        if device_definitions["routers"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/routers")
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/routers/tasks")
        for router in device_definitions["routers"]:
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + router["name"])
            os.mkdir(OUTPUT_DIRECTORY + "/" + directory + "/roles/" + router["name"] + "/tasks")

    except FileExistsError:
        pass
    except IOError:
        print("Could not create directories for provisioning.")
        raise



def prepare_directories(device_definitions):
    """ Prepares the necessary directory structure. """

    shutil.rmtree(OUTPUT_DIRECTORY, True)
    
    try:
        os.mkdir(OUTPUT_DIRECTORY)
    except IOError:
        print("Could not create directory ./" + OUTPUT_DIRECTORY + ".")
        raise

    _create_provisioning_directories("base_provisioning", device_definitions)
    _create_provisioning_directories("provisioning", device_definitions)
    

    
    

