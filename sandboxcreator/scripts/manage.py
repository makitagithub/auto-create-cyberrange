#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List, Optional

from sandboxcreator import manager


def _parse_cli_args(cli_args: List[str]) -> argparse.ArgumentParser:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument("command",
                        help="command to be executed",
                        choices=["build", "destroy"])
    parser.add_argument("-d", "--vagrantfile-directory",
                        help="path to a directory containing a Vagrantfile",
                        default=os.getcwd())
    parser.add_argument("-m", "--machines",
                        help="list of machines involved",
                        nargs='*',
                        default=[])
    parser.add_argument("-o", "--out",
                        help="command line output",
                        choices=["devnull", "stdout"],
                        default="stdout")
    parser.add_argument("-e", "--err",
                        help="command line error output",
                        choices=["devnull", "stdout"],
                        default="stdout")

    return parser.parse_args(cli_args)


def _print_message(command: manager.Command,
                   exception: Optional[Exception] = None) -> None:
    """Print final message about success or failure"""

    if exception is None:
        if command is manager.Command.BUILD:
            print("\nSandbox was successfully built")
        elif command is manager.Command.DESTROY:
            print("\nSandbox was successfully destroyed")
    else:
        if command is manager.Command.BUILD:
            print(f"\nSandbox building process has failed:\n{exception}")
        elif command is manager.Command.DESTROY:
            print(f"\nSandbox destroying process has failed:\n{exception}")


def _translate_str_command(command_str: str) -> manager.Command:
    """Translate string commands to enum"""

    if command_str == "build":
        return manager.Command.BUILD
    if command_str == "destroy":
        return manager.Command.DESTROY
    raise ValueError(f"Invalid command: {command_str}")


def _translate_str_output(output_str: str) -> manager.Output:
    """Translate string output device to enum"""

    if output_str == "devnull":
        return manager.Output.DEVNULL
    if output_str == "stdout":
        return manager.Output.STDOUT
    raise ValueError(f"Invalid output device: {output_str}")


def _run_manager(cli_args: argparse.ArgumentParser) -> None:
    try:
        command: manager.Command = _translate_str_command(cli_args.command)
        output_dev: manager.Output = _translate_str_output(cli_args.out)
        error_dev: manager.Output = _translate_str_output(cli_args.err)

        manager.manage(command, cli_args.vagrantfile_directory,
                       cli_args.machines, output_dev, error_dev)
    except Exception as error:
        _print_message(command, error)
        sys.exit(1)

    _print_message(command)


def main():
    parsed_args: argparse.ArgumentParser = _parse_cli_args(sys.argv[1:])
    _run_manager(parsed_args)


if __name__ == '__main__':
    main()
