import jinja2
from pathlib import Path


class Writer:
    """Static methods for generating files"""

    TEMPLATE_DIR: Path = Path(__file__).parent / "resources/templates"

    @staticmethod
    def _write_to_file(filepath: Path, content: str) -> None:
        """Generate a file from output string."""
        try:
            with open(filepath, "w") as new_file:
                new_file.write(content)
        except IOError:
            raise IOError(f"Could not create file {filepath}")

    @staticmethod
    def generate_file_from_template(output_file: Path, template_name: str,
                                    **data) -> None:
        """Generate file from Jinja2 template

        :param output_file: path to the output file
        :param template_name: name of a Jinja2 template file in templates dir
        :param data: arbitrary number of named args for the template
        """

        try:
            template_loader = jinja2.FileSystemLoader(searchpath=
                                                      Writer.TEMPLATE_DIR)
            template_env = jinja2.Environment(loader=template_loader,
                                          trim_blocks=True,
                                          lstrip_blocks=True)
            template = template_env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise RuntimeError(f"Could not find template {template_name}")

        output = template.render(**data)
        Writer._write_to_file(output_file, output)
