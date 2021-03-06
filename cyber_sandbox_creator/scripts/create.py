#!/usr/bin/env python3

import argparse
import sys

from cyber_sandbox_creator import creator

parser = argparse.ArgumentParser()

parser.add_argument("topology_file",
                    help="path to the topology definition")
parser.add_argument("-o", "--output-dir",
                    help="output directory for the sandbox", action="store")
parser.add_argument("-a", "--ansible-installed",
                    help="uses Ansible installed on the host machine",
                    action="store_true")
parser.add_argument("-b", "--border-router",
                    help="create a border router", action="store_true")
parser.add_argument("-r", "--rewrite-provisioning",
                    help="generate clean user provisioning even if it exists",
                    action="store_true")
parser.add_argument("-p", "--provisioning-dir",
                    help="path to directory with user provisioning files",
                    action="store")
parser.add_argument("-e", "--extra-vars",
                    help="path to file with extra_vars for Ansible",
                    action="store")

args = parser.parse_args()

if args.output_dir:
    output_dir: str = args.output_dir
else:
    output_dir: str = "sandbox"

try:
    creator.create(args.topology_file, output_dir, args.ansible_installed,
                   args.border_router, args.provisioning_dir, args.extra_vars,
                   args.rewrite_provisioning)
except (ValueError, IOError) as e:
    print(f"Could not create intermediate sandbox definition:\n{e}")
    sys.exit(1)

print("Intermediate sandbox definition was successfully created")
