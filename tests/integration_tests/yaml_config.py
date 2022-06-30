"""Contains auxiliary functions for integration testing that allow reading information from configuration file."""

import yaml
import sys

def get_output_dir(config_file):
    """Read and print value for output_directory or print default value."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(config_file) as f:
        doc = yaml.safe_load(f)

    if 'output_directory' in doc:
        print(doc['output_directory'], file=stdout)
    else:
        print("test_output", file=stdout)

def get_topology_files(config_file):
    """Read and print values for file for all topologies."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(config_file) as f:
        doc = yaml.safe_load(f)
    for topology in doc['topologies']:
        if 'file' in topology:
            print(topology['file'], file=stdout)

def get_topology_arguments(config_file, topology_file):
    """Read and print all values for arguments for a given topology."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(config_file) as f:
        doc = yaml.safe_load(f)

    for topology in doc['topologies']:
        if topology['file'] == topology_file:
            if 'arguments' in topology:
                for argument in topology['arguments']:
                    if isinstance(argument, list):
                        print("--"+' --'.join(argument), file=stdout)
                    elif argument == 'no-arguments':
                        print(" ", file=stdout)
                    else:
                        print("--"+argument, file=stdout)
                    
def get_topology_boxes(config_file, topology_file):
    """Read and print all values for boxes for a given topology. Based on original_boxes value optionally also prints 'no-box'."""
    stdout = open(sys.__stdout__.fileno(),
        mode=sys.__stdout__.mode,
        buffering=1,
        encoding=sys.__stdout__.encoding,
        errors=sys.__stdout__.errors,
        newline='\n',
        closefd=False)

    with open(config_file) as f:
        doc = yaml.safe_load(f)

    for topology in doc['topologies']:
        if topology['file'] == topology_file:
            if 'boxes' in topology:
                if 'original_boxes' not in topology:
                    print("no-box", file=stdout)
                elif topology['original_boxes'] == True:
                    print("no-box", file=stdout)
                for box in topology['boxes']:
                    print(box, file=stdout)
            else:
                print("no-box", file=stdout)