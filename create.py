#!/usr/bin/python3
""" A script that generates a Vagrantfile from yaml. """

import sys
import jinja2

from modules.file_generator import generate_vagrantfile, generate_ansible_files
from modules.device_creator import open_file

if len(sys.argv) != 2:
    print("Error: Expecting 1 argument (yml file).")
    sys.exit()

device_definitions = open_file(str(sys.argv[1]))

generate_vagrantfile(device_definitions)
generate_ansible_files(device_definitions)

