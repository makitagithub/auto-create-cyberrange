#!/usr/bin/python3

import sys
import jinja2

from modules.device_creator import create_devices

if (len(sys.argv) != 2):
    print ("Error: Expecting 1 argument (yml file).")
    sys.exit();

# A structure with formatted commands for each device
devices = create_devices(str(sys.argv[1]))

# Generating output via Jinja2
templateLoader = jinja2.FileSystemLoader(searchpath="templates")
templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
baseTemplate = templateEnv.get_template("base")
output = baseTemplate.render(devices = devices)

print (output)

