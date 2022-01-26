import unittest
from sandboxcreator.scripts import create


class DefaultCLIArgsTests(unittest.TestCase):
    """Default CLI arguments check"""

    def setUp(self) -> None:
        self.args = create._parse_cli_args(["topology.yml"])

    def test_default_output_dir(self):
        self.assertEqual("", self.args.output_dir)

    def test_default_ansible_installed(self):
        self.assertFalse(self.args.ansible_installed)

    def test_default_rewrite_provisioning(self):
        self.assertFalse(self.args.rewrite_provisioning)

    def test_default_provisioning_dir(self):
        self.assertEqual("", self.args.provisioning_dir)

    def test_default_extra_vars(self):
        self.assertEqual("", self.args.extra_vars)

    def test_default_verbose_ansible(self):
        self.assertFalse(self.args.verbose_ansible)


class ValueCLIArgsTests(unittest.TestCase):
    """Correct non-default CLI arguments check"""

    def test_value_topology_file(self):
        args = create._parse_cli_args(["topology.yml"])
        self.assertEqual("topology.yml", args.topology_file)

    def test_value_output_dir_short(self):
        args = create._parse_cli_args(["-o", "test", "topology.yml"])
        self.assertEqual("test", args.output_dir)

    def test_value_output_dir_long(self):
        args = create._parse_cli_args(["--output-dir", "test", "topology.yml"])
        self.assertEqual("test", args.output_dir)

    def test_value_ansible_installed_short(self):
        args = create._parse_cli_args(["-a", "topology.yml"])
        self.assertTrue(args.ansible_installed)

    def test_value_ansible_installed_long(self):
        args = create._parse_cli_args(["--ansible-installed", "topology.yml"])
        self.assertTrue(args.ansible_installed)

    def test_value_rewrite_provisioning(self):
        args = create._parse_cli_args(["--rewrite-provisioning",
                                       "topology.yml"])
        self.assertTrue(args.rewrite_provisioning)

    def test_value_provisioning_dir(self):
        args = create._parse_cli_args(["--provisioning-dir", "test",
                                       "topology.yml"])
        self.assertEqual("test", args.provisioning_dir)

    def test_value_extra_vars(self):
        args = create._parse_cli_args(["--extra-vars", "test", "topology.yml"])
        self.assertEqual("test", args.extra_vars)

    def test_value_verbose_ansible(self):
        args = create._parse_cli_args(["--verbose-ansible", "topology.yml"])
        self.assertTrue(args.verbose_ansible)
