import subprocess
from pathlib import Path
from typing import List
from unittest import TestCase

from sandboxcreator import manager


class TestInputValidation(TestCase):
    TEST_DIR_PATH: Path = Path(__file__).parent.joinpath("resources")
    TEST_DIR_STR: str = TEST_DIR_PATH.as_posix()
    MISSING_DIR_PATH: Path = Path("missing_dir")
    MISSING_DIR_STR: str = "missing_dir"

    # _validate_command_name
    def test_validate_command_name_valid(self):
        output: manager.Command = manager._validate_command_name(
            manager.Command.BUILD)
        self.assertEqual(manager.Command.BUILD, output)

    def test_validate_command_name_invalid(self):
        with self.assertRaises(TypeError):
            manager._validate_command_name(1)

    # _process_vagrantfile_location
    def test_process_vagrantfile_location_valid_str(self):
        output: Path = manager._process_vagrantfile_location(self.TEST_DIR_STR)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_vagrantfile_location_valid_path(self):
        output: Path = manager._process_vagrantfile_location(self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_vagrantfile_location_invalid_empty(self):
        with self.assertRaises(ValueError):
            manager._process_vagrantfile_location("")

    def test_process_vagrantfile_location_invalid_int(self):
        with self.assertRaises(TypeError):
            manager._process_vagrantfile_location(1)

    def test_process_vagrantfile_location_invalid_missing_dir(self):
        with self.assertRaises(ValueError):
            manager._process_vagrantfile_location(self.MISSING_DIR_STR)

    def test_process_vagrantfile_location_invalid_missing_vf(self):
        with self.assertRaises(ValueError):
            manager._process_vagrantfile_location(self.TEST_DIR_PATH.parent)

    # _process_machines_list
    def test_process_machines_list_valid(self):
        machines: List[str] = ["machine1", "machine2"]
        checked: List[str] = manager._process_machines_list(machines)
        self.assertEqual(machines, checked)

    def test_process_machines_list_invalid_not_list(self):
        with self.assertRaises(TypeError):
            manager._process_machines_list("machine1")

    def test_process_machines_list_invalid_not_str_list(self):
        with self.assertRaises(TypeError):
            manager._process_machines_list([1, 2])

    # _validate_cli_output
    def test_validate_cli_output_valid(self):
        checked = manager._validate_cli_output(manager.Output.DEVNULL)
        self.assertEqual(manager.Output.DEVNULL, checked)

    def test_validate_cli_output_invalid_type(self):
        with self.assertRaises(TypeError):
            manager._validate_cli_output(1)

    # _generate_cli_command
    def test_generate_cli_command_valid_build_wo_machines(self):
        command = manager.Command.BUILD
        cli_command: List[str] = manager._generate_cli_command(command, [])
        self.assertEqual(['vagrant', 'up'], cli_command)

    def test_generate_cli_command_valid_build_1_machine(self):
        command = manager.Command.BUILD
        cli_command: List[str] = manager._generate_cli_command(command,
                                                               ['machine1'])
        self.assertEqual(['vagrant', 'up', 'machine1'], cli_command)

    def test_generate_cli_command_valid_build_2_machines(self):
        command = manager.Command.BUILD
        cli_command: List[str] = manager._generate_cli_command(command,
                                                               ['machine1',
                                                                'machine2'])
        self.assertEqual(['vagrant', 'up', 'machine1', 'machine2'], cli_command)

    def test_generate_cli_command_valid_destroy_wo_machines(self):
        command = manager.Command.DESTROY
        cli_command: List[str] = manager._generate_cli_command(command, [])
        self.assertEqual(['vagrant', 'destroy', '-f'], cli_command)

    def test_generate_cli_command_valid_destroy_1_machine(self):
        command = manager.Command.DESTROY
        cli_command: List[str] = manager._generate_cli_command(command,
                                                               ['machine1'])
        self.assertEqual(['vagrant', 'destroy', '-f', 'machine1'], cli_command)

    def test_generate_cli_command_valid_destroy_2_machines(self):
        command = manager.Command.DESTROY
        cli_command: List[str] = manager._generate_cli_command(command,
                                                               ['machine1',
                                                                'machine2'])
        self.assertEqual(['vagrant', 'destroy', '-f', 'machine1', 'machine2'],
                         cli_command)

    def test_generate_cli_command_invalid_type(self):
        with self.assertRaises(ValueError):
            manager._generate_cli_command(1, [])

    # _translate_output
    def test_translate_output_valid_devnull(self):
        output = manager._translate_output(manager.Output.DEVNULL)
        self.assertEqual(subprocess.DEVNULL, output)

    def test_translate_output_valid_stdout(self):
        output = manager._translate_output(manager.Output.STDOUT)
        self.assertEqual(None, output)

    def test_translate_output_invalid_type(self):
        with self.assertRaises(ValueError):
            manager._translate_output(1)
