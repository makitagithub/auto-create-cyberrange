""" This module contains functions to parse input arguments. """

import argparse

def parse_input_args(argv, flags):
    """ 
    Parses the given input arguments for input file name and flags.

    :param argv: input arguments (list of strings)
    :param flags: dictionary to write the parsed flags
    :returns: name of the input file
    """

    input_file_name = None
    parser = argparse.ArgumentParser()

    parser.add_argument("definition_file", help="path to the input yaml definition")
    parser.add_argument("--ansible_local", help="uses ansible_local for provisioning instead of ansible", action="store_true")
    parser.add_argument("--verbose_ansible", help="sets verbose output for ansible (-vvvv)", action="store_true")
    parser.add_argument("--border_router", help="creates a border router with connection to all routers", action="store_true")
    args = parser.parse_args()

    input_file_name = args.definition_file
    flags["ansible_local"] = args.ansible_local
    flags["verbose_ansible"] = args.verbose_ansible
    flags["border_router"] = args.border_router

    return input_file_name
