from typing import List, Optional

from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_metadata import PythonPackageMetadata

from automation_scripts.configuration.project_metadata import ProjectMetadata


class PythonDevelopmentConfiguration:


    def __init__(self, venv_directory: str, package_collection: List[PythonPackage], pip_configuration_file_path: Optional[str]) -> None:
        self.venv_directory = venv_directory
        self.package_collection = package_collection
        self.pip_configuration_file_path = pip_configuration_file_path


    def get_package_metadata(self, project_metadata: ProjectMetadata) -> PythonPackageMetadata:
        return PythonPackageMetadata(
            product_identifier = project_metadata.identifier,
            version_identifier = project_metadata.version.full_identifier,
            revision_date = project_metadata.version.revision_date,
            copyright_text = project_metadata.copyright_text,
        )
