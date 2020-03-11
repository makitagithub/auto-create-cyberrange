#!/usr/bin/python3
"""
This script generates a Vagrantfile and ansible files from a YAML definition
of virtual machines and network topology.  See the documentation for details.
"""

import sys

from modules.ansible_generator import generate_playbooks
from modules.vagrant_generator import generate_vagrantfile
from modules.file_manager import open_yaml, prepare_directories
from modules.input_argument_parser import parse_input_args
from modules.input_file_validator import validate_device_definitions
from modules.preprocessing import preprocess


""" Parsing the input arguments. """
flags = dict()

try:
    input_file_name = parse_input_args(sys.argv, flags)
except Exception:
    print("Input arguments could not be parsed.")
    sys.exit(1)

""" Parsing the definitions file. """
try:
    device_definitions = open_yaml(input_file_name)
except Exception:
    print("Definitions file could not be parsed.")
    sys.exit(1)

""" Validating device definitions. """
try:
    validate_device_definitions(device_definitions)
except Exception:
    print("Device definition validation was not sussessful.")
    sys.exit(1)

""" Preprocessing the definitions before device creation. """
try:
    preprocess(device_definitions, flags)
except Exception:
    print("Preprocessing was not successful.")
    sys.exit(1)

""" Preparing the directory structure. """
try:
    prepare_directories(device_definitions)
except Exception:
    print("Directory structure was not created.")
    sys.exit(1)

""" Generating Vagrantfile. """
try:
    generate_vagrantfile(device_definitions, flags)
except Exception:
    print("Vagrantfile was not created.")
    sys.exit(1)

""" Generating ansible playbooks. """
try:
    generate_playbooks(device_definitions, flags)
except Exception:
    print("Playbooks could not be created.")
    sys.exit(1)
