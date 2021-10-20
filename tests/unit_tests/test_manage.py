import argparse
import os
import unittest
from sandboxcreator.scripts import manage


class DefaultCLIArgsTests(unittest.TestCase):
    """Default CLI arguments check"""

    def setUp(self) -> None:
        self.args = manage._parse_cli_args(["build"])

    def test_default_vagrantfile_directory(self):
        self.assertEqual(os.getcwd(), self.args.vagrantfile_directory)

    def test_default_machines(self):
        self.assertEqual([], self.args.machines)

    def test_default_verbose(self):
        self.assertFalse(self.args.verbose)

    def test_default_out(self):
        self.assertEqual("devnull", self.args.out)

    def test_default_err(self):
        self.assertEqual("stdout", self.args.err)


class ValueCLIArgsTests(unittest.TestCase):
    """Correct non-default CLI arguments check"""

    def test_value_command(self):
        args = manage._parse_cli_args(["build"])
        self.assertEqual("build", args.command)

    def test_value_vagrantfile_directory_short(self):
        args = manage._parse_cli_args(["build", "-d", "sandbox"])
        self.assertEqual("sandbox", args.vagrantfile_directory)

    def test_value_vagrantfile_directory_long(self):
        args = manage._parse_cli_args(["build", "--vagrantfile-directory",
                                       "sandbox"])
        self.assertEqual("sandbox", args.vagrantfile_directory)

    def test_value_machines_1_short(self):
        args = manage._parse_cli_args(["build", "-m", "machine1"])
        self.assertEqual(["machine1"], args.machines)

    def test_value_machines_1_long(self):
        args = manage._parse_cli_args(["build", "--machines", "machine1"])
        self.assertEqual(["machine1"], args.machines)

    def test_value_machines_2_short(self):
        args = manage._parse_cli_args(["build", "-m", "machine1", "machine2"])
        self.assertEqual(["machine1", "machine2"], args.machines)

    def test_value_machines_2_long(self):
        args = manage._parse_cli_args(["build", "--machines", "machine1",
                                       "machine2"])
        self.assertEqual(["machine1", "machine2"], args.machines)

    def test_value_verbose_short(self):
        args = manage._parse_cli_args(["build", "-v"])
        self.assertTrue(args.verbose)

    def test_value_verbose_long(self):
        args = manage._parse_cli_args(["build", "--verbose"])
        self.assertTrue(args.verbose)

    def test_value_out_short_valid_devnull(self):
        args = manage._parse_cli_args(["build", "-o", "devnull"])
        self.assertEqual("devnull", args.out)

    def test_value_out_long_valid_devnull(self):
        args = manage._parse_cli_args(["build", "--out", "devnull"])
        self.assertEqual("devnull", args.out)

    def test_value_out_short_valid_stdout(self):
        args = manage._parse_cli_args(["build", "-o", "stdout"])
        self.assertEqual("stdout", args.out)

    def test_value_out_long_valid_stdout(self):
        args = manage._parse_cli_args(["build", "--out", "stdout"])
        self.assertEqual("stdout", args.out)
