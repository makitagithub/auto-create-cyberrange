"""Contains auxiliary functions for integration testing that allow reading information from configuration file."""

import yaml

def get_output_dir(config_file):
    """Read and print value for output_directory or print default value."""
    with open(config_file) as f:
        doc = yaml.safe_load(f)

    if 'output_directory' in doc:
        print(doc['output_directory'])
    else:
        print("./test_output")

def get_topology_files(config_file):
    """Read and print values for file for all topologies."""
    with open(config_file) as f:
        doc = yaml.safe_load(f)
    for topology in doc['topologies']:
        if 'file' in topology:
            print(topology['file'])

def get_topology_arguments(config_file, topology_file):
    """Read and print all values for arguments for a given topology."""
    with open(config_file) as f:
        doc = yaml.safe_load(f)

    for topology in doc['topologies']:
        if topology['file'] == topology_file:
            if 'arguments' in topology:
                for argument in topology['arguments']:
                    if isinstance(argument, list):
                        print("--"+' --'.join(argument))
                    elif argument == 'no-arguments':
                        print(" ")
                    else:
                        print("--"+argument)
                    
def get_topology_boxes(config_file, topology_file):
    """Read and print all values for boxes for a given topology. Based on original_boxes value optionally also prints 'no-box'."""
    with open(config_file) as f:
        doc = yaml.safe_load(f)

    for topology in doc['topologies']:
        if topology['file'] == topology_file:
            if 'boxes' in topology:
                if 'original_boxes' not in topology:
                    print("no-box")
                elif topology['original_boxes'] == True:
                    print("no-box")
                for box in topology['boxes']:
                    print(box)
            else:
                print("no-box")