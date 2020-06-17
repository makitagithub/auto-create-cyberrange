#!/usr/bin/python3
"""Generates Vagrantfile from YAML definition.

Generate a Vagrantfile and ansible files from a YAML definition of virtual
machines and network topology. See the documentation for details.
"""

from modules.ansible_generator import generate_playbooks
from modules.vagrant_generator import generate_vagrantfile
from modules.file_manager import open_yaml, prepare_directories
from modules.input_argument_parser import parse_input_args
from modules.input_file_validator import validate_device_definitions
from modules.preprocessing import preprocess


INPUT_FILE_NAME, FLAGS = parse_input_args()
device_definitions = open_yaml(INPUT_FILE_NAME)

validate_device_definitions(device_definitions)
preprocess(device_definitions, FLAGS)
prepare_directories(device_definitions)

generate_vagrantfile(device_definitions, FLAGS)
generate_playbooks(device_definitions, FLAGS)

print("Sandbox was successfully created.")
