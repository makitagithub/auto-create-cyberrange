from enum import Enum
from pathlib import Path
import subprocess
from typing import List, Union


class Command(Enum):
    """Manager commands"""
    BUILD = 1
    DESTROY = 2


class Output(Enum):
    """Manager output devices"""
    DEVNULL = 1
    STDOUT = 2


def _validate_command_name(command: Command) -> Command:
    """Validate the command name"""

    if not isinstance(command, Command):
        raise TypeError("Invalid command type")

    return command


def _process_vagrantfile_location(vagrantfile_location: Union[str, Path]) \
        -> Path:
    """Validate and resolve path to directory containing Vagrantfile"""

    try:
        if isinstance(vagrantfile_location, str):
            if vagrantfile_location == "":
                raise ValueError("Vagrantfile location cannot be empty")
            vagrantfile_dir_path: Path = Path(vagrantfile_location).resolve()
        elif isinstance(vagrantfile_location, Path):
            vagrantfile_dir_path: Path = vagrantfile_location.resolve()
        else:
            raise TypeError("Vagrantfile location has invalid type "
                            f"\"{type(vagrantfile_location)}\"")
        if not vagrantfile_dir_path.is_dir():
            raise IOError(f"Directory {vagrantfile_dir_path} does not exist")
        if not vagrantfile_dir_path.joinpath("Vagrantfile").is_file():
            raise IOError(f"Directory {vagrantfile_dir_path} does not contain Vagrantfile")
    except OSError:
        raise ValueError("Invalid path to Vagrantfile directory"
                         f"\"{vagrantfile_location}\"")

    return vagrantfile_dir_path


def _process_machines_list(machines: List[str]) -> List[str]:
    """Validate the list of machines"""

    if not isinstance(machines, List):
        raise TypeError("List of machines must be a List")
    for machine in machines:
        if not isinstance(machine, str):
            raise TypeError("Machine names must be strings")

    return machines


def _validate_cli_output(output: Output) -> Output:
    """Validate output device"""

    if not isinstance(output, Output):
        raise TypeError("Invalid output type")

    return output


def _generate_cli_command(command: Command, machines_list: List[str]) \
        -> List[str]:
    """Generate CLI command for Vagrant"""

    cli_command: List[str] = ["vagrant"]
    if command is Command.BUILD:
        cli_command.append("up")
    elif command is Command.DESTROY:
        cli_command += ["destroy", "-f"]
    cli_command += machines_list

    return cli_command


def _translate_output(output: Output):
    """Translate Output enum values to subprocess values"""

    if output is Output.DEVNULL:
        return subprocess.DEVNULL
    if output is Output.STDOUT:
        return None

    raise AttributeError("Invalid output device")


def _execute_cli_command(cli_command: List[str], vagrantfile_dir: Path,
                         output: Output, error: Output):
    """Execute Vagrant CLI command"""

    subprocess.run(cli_command, cwd=vagrantfile_dir, check=True,
                   stdout=_translate_output(output),
                   stderr=_translate_output(error))


def manage(command: Command, vagrantfile_location: Union[str, Path],
           machines: List[str] = [], output: Output = Output.DEVNULL,
           error: Output = Output.DEVNULL):
    """Vagrant wrapper to simplify sandbox instantiation and manipulation.

    :param command: type of desired manipulation (build, destroy, ...)
    :param vagrantfile_location: path to a directory containing Vagrantfile
    :param machines: list of involved machine names
    :param output: where to dump the command line output (devnull, stdout, ...)
    :param error: where to dump the command line error output (stdout, ...)
    """

    command_name: Command = _validate_command_name(command)
    vagrantfile_dir: Path = _process_vagrantfile_location(vagrantfile_location)
    machines_list: List[str] = _process_machines_list(machines)
    cli_output: Output = _validate_cli_output(output)
    cli_error: Output = _validate_cli_output(error)

    cli_command: List[str] = _generate_cli_command(command_name, machines_list)

    _execute_cli_command(cli_command, vagrantfile_dir, cli_output, cli_error)
