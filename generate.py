#!/usr/bin/python3
""" A script that generates a Vagrantfile from yaml. """

import sys
import jinja2

from modules.device_creator import create_devices, create_vagrantfile

if len(sys.argv) != 2:
    print("Error: Expecting 1 argument (yml file).")
    sys.exit()

# A structure with formatted commands for each device
DEVICES = create_devices(str(sys.argv[1]))

# Generating output via Jinja2
TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath="templates")
TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER, trim_blocks=True)
BASE_TEMPLATE = TEMPLATE_ENV.get_template("base")
OUTPUT = BASE_TEMPLATE.render(devices=DEVICES)

create_vagrantfile(OUTPUT)
