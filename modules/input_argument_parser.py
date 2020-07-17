"""This module contains functions to parse input arguments."""

import argparse


def parse_input_args():
    """Parse the given input arguments for input file name and flags.

    :returns: name of the input file and flags
    """

    input_file_name = None
    flags = dict()
    parser = argparse.ArgumentParser()

    parser.add_argument("definition_file",
                        help="path to the input yaml definition")
    parser.add_argument("--ansible_local",
                        help="uses ansible_local for provisioning instead "
                        "of ansible", action="store_true")
    parser.add_argument("--verbose_ansible",
                        help="sets verbose output for ansible (-vv)",
                        action="store_true")
    parser.add_argument("--border_router",
                        help="creates a border router with connection to "
                        "all routers", action="store_true")
    parser.add_argument("--provisioning_dir",
                        help="path to directory with user provisioning files",
                        action="store")
    parser.add_argument("--extra_vars",
                        help="path to file with extra_vars for ansible",
                        action="store")

    args = parser.parse_args()

    input_file_name = args.definition_file
    flags["ansible_local"] = args.ansible_local
    flags["verbose_ansible"] = args.verbose_ansible
    flags["border_router"] = args.border_router
    flags["provisioning_dir"] = args.provisioning_dir
    flags["extra_vars"] = args.extra_vars

    return input_file_name, flags
