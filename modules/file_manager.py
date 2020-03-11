""" This module handles file imports and creations in general. """

import jinja2
import yaml

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

def generate_file(filename, output_string):
    """
    Generates a file from output string.
    
    :param filename: name of the file to create
    :param output_string: string to write to the file
    """

    try:
        new_file = open(filename, "w")
        new_file.write(output_string)
    except IOError:
        print("Error: cannot write to this location.")
        raise

def load_template(template_name):
    """
    Returns a loaded jinja2 template.
    
    :param template_name: name of the template file
    """

    template_loader = jinja2.FileSystemLoader(searchpath="templates")
    template_env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    return template_env.get_template(template_name)
