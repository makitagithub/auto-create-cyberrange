""" This module contains functions to parse input arguments. """

def parse_input_args(argv, flags):
    """ 
    Parses the given input arguments for input file name and flags.

    :param argv: input arguments (list of strings)
    :param flags: dictionary to write the parsed flags
    :returns: name of the input file
    :raise AttributeError: invalid number of args or unknown flag
    """

    input_file_name = None

    if len(argv) == 3:
        if str(argv[1]) == "-l":
            flags["ansible_local"] = True
            input_file_name = str(argv[2])
        elif str(argv[2]) == "-l":
            flags["ansible_local"] = True
            input_file_name = str(argv[1])
        else:
            print("Error: Expecting a yml file and optionally a flag -l.")
            raise AttributeError
    elif len(argv) == 2:
        input_file_name = str(argv[1])
    else:
        print("Error: Expecting a yml file and optionally a flag -l.")
        raise AttributeError

    return input_file_name
