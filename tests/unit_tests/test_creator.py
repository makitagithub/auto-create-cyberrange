from unittest import TestCase
from pathlib import Path

from cyber_sandbox_creator import creator


class TestInputValidation(TestCase):
    TEST_DIR_PATH: Path = Path(__file__).parent.joinpath("resources")
    TEST_DIR_STR: str = TEST_DIR_PATH.as_posix()
    TEST_FILE_PATH: Path = TEST_DIR_PATH.joinpath("test_file.yml")
    TEST_FILE_STR: str = TEST_FILE_PATH.as_posix()
    MISSING_FILE_PATH: Path = Path("missing_file")
    MISSING_FILE_STR: str = "missing_file"

    # _process_topology_path
    def test_process_topology_path_valid_str(self):
        output: Path = creator._process_topology_path(self.TEST_FILE_STR)
        self.assertEqual(Path(self.TEST_FILE_STR).resolve(), output)

    def test_process_topology_path_valid_path(self):
        output: Path = creator._process_topology_path(self.TEST_FILE_PATH)
        self.assertEqual(self.TEST_FILE_PATH.resolve(), output)

    def test_process_topology_path_invalid_type_int(self):
        with self.assertRaises(TypeError):
            creator._process_topology_path(1)

    def test_process_topology_path_invalid_type_none(self):
        with self.assertRaises(TypeError):
            creator._process_topology_path()

    def test_process_topology_path_missing_file_str(self):
        with self.assertRaises(ValueError):
            creator._process_topology_path(self.MISSING_FILE_STR)

    def test_process_topology_path_invalid_file(self):
        with self.assertRaises(ValueError):
            creator._process_topology_path(self.TEST_FILE_PATH.parent)

    # _process_output_path
    def test_process_output_path_valid_none(self):
        output: Path = creator._process_output_path(None, self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH.parent.joinpath("sandbox"), output)

    def test_process_output_path_valid_empty(self):
        output: Path = creator._process_output_path("", self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH.parent.joinpath("sandbox"), output)

    def test_process_output_path_valid_path(self):
        output: Path = creator._process_output_path(self.TEST_DIR_PATH,
                                                    self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_output_path_valid_str(self):
        output: Path = creator._process_output_path(
            self.TEST_DIR_PATH.as_posix(), self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_output_path_invalid_type(self):
        with self.assertRaises(TypeError):
            creator._process_output_path(1, self.TEST_DIR_PATH)

    def test_process_output_path_invalid_file(self):
        with self.assertRaises(ValueError):
            creator._process_output_path(self.TEST_FILE_PATH,
                                         self.TEST_DIR_PATH)

    # _process_provisioning_path
    def test_process_provisioning_path_valid_none(self):
        output = creator._process_provisioning_path(None)
        self.assertEqual(None, output)

    def test_process_provisioning_path_valid_empty(self):
        output = creator._process_provisioning_path("")
        self.assertEqual(None, output)

    def test_process_provisioning_path_valid_path(self):
        output = creator._process_provisioning_path(self.TEST_DIR_PATH)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_provisioning_path_valid_str(self):
        output = creator._process_provisioning_path(self.TEST_DIR_STR)
        self.assertEqual(self.TEST_DIR_PATH, output)

    def test_process_provisioning_path_invalid_type(self):
        with self.assertRaises(TypeError):
            creator._process_provisioning_path(1)

    def test_process_provisioning_path_invalid_not_dir(self):
        with self.assertRaises(ValueError):
            creator._process_provisioning_path(self.TEST_FILE_PATH)

    def test_process_provisioning_path_invalid_without_playbook(self):
        with self.assertRaises(ValueError):
            creator._process_provisioning_path(self.TEST_DIR_PATH.parent)

    # _process_extra_vars_path
    def test_process_extra_vars_path_valid_none(self):
        output = creator._process_extra_vars_path(None)
        self.assertEqual(None, output)

    def test_process_extra_vars_path_valid_empty(self):
        output = creator._process_extra_vars_path("")
        self.assertEqual(None, output)

    def test_process_extra_vars_path_valid_path(self):
        output: Path = creator._process_extra_vars_path(self.TEST_FILE_PATH)
        self.assertEqual(self.TEST_FILE_PATH, output)

    def test_process_extra_vars_path_valid_str(self):
        output: Path = creator._process_extra_vars_path(self.TEST_FILE_STR)
        self.assertEqual(self.TEST_FILE_PATH, output)

    def test_process_extra_vars_path_invalid_type(self):
        with self.assertRaises(TypeError):
            creator._process_extra_vars_path(1)

    def test_process_extra_vars_path_invalid_missing(self):
        with self.assertRaises(ValueError):
            creator._process_extra_vars_path(self.MISSING_FILE_STR)
