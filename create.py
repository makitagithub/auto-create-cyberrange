#!/usr/bin/python3
"""
This script generates a Vagrantfile and ansible files from a YAML definition
of virtual machines and network topology.  See the documentation for details.
"""

import sys

from modules.file_generator import generate_vagrantfile, generate_ansible_files
from modules.device_creator import open_file
from modules.routing import create_border_router
from modules.input_argument_parser import parse_input_args
from modules.input_file_validator import validate_device_definitions


""" Parsing the input arguments. """
flags = dict()

try:
    input_file_name = parse_input_args(sys.argv, flags)
except Exception:
    print("Input arguments could not be parsed.")
    sys.exit(1)

""" Parsing the definitions file. """
try:
    device_definitions = open_file(input_file_name)
except Exception:
    print("Definitions file could not be parsed.")
    sys.exit(1)

""" Validating device definitions. """
try:
    validate_device_definitions(device_definitions)
except Exception:
    print("Device definition validation was not sussessful.")
    sys.exit(1)


# TODO

create_border_router(device_definitions)
if "ansible_local" in flags and flags["ansible_local"]:
    generate_vagrantfile(device_definitions, True)
else:
    generate_vagrantfile(device_definitions, False)

generate_ansible_files(device_definitions)
