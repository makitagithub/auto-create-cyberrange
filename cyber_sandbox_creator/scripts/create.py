#!/usr/bin/env python3

import argparse
import sys
from typing import List

from cyber_sandbox_creator.creator import create


def _parse_cli_args(cli_args: List[str]) -> argparse.ArgumentParser:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument("topology_file",
                        help="path to the topology definition")
    parser.add_argument("-o", "--output-dir",
                        help="output directory for the sandbox",
                        default="",
                        action="store")
    parser.add_argument("-a", "--ansible-installed",
                        help="use Ansible installed on the host machine",
                        action="store_true")
    parser.add_argument("-b", "--border-router",
                        help="create a border router",
                        action="store_true")
    parser.add_argument("--rewrite-provisioning",
                        help="always generate clean user provisioning",
                        action="store_true")
    parser.add_argument("--provisioning-dir",
                        help="path to directory with user provisioning files",
                        default="",
                        action="store")
    parser.add_argument("--extra-vars",
                        help="path to file with extra_vars for Ansible",
                        default="",
                        action="store")
    parser.add_argument("--verbose-ansible",
                        help="set verbose output for Ansible (-vv)",
                        action="store_true")

    return parser.parse_args(cli_args)


if __name__ == '__main__':
    args: argparse.ArgumentParser = _parse_cli_args(sys.argv[1:])

    try:
        create(args.topology_file, args.output_dir, args.ansible_installed,
               args.border_router, args.provisioning_dir, args.extra_vars,
               args.rewrite_provisioning, args.verbose_ansible)
    except (ValueError, IOError) as e:
        print(f"Could not create intermediate sandbox definition:\n{e}")
        sys.exit(1)

    print("Intermediate sandbox definition was successfully created")
