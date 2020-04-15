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


flags = dict()
input_file_name = parse_input_args(sys.argv, flags)
device_definitions = open_yaml(input_file_name)

validate_device_definitions(device_definitions)
preprocess(device_definitions, flags)
prepare_directories(device_definitions)

generate_vagrantfile(device_definitions, flags)
generate_playbooks(device_definitions, flags)

print("Sandbox was successfully created.")
