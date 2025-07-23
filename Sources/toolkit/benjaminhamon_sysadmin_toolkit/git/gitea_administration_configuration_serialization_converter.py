# cspell:words gitea

from typing import Any

from benjaminhamon_standard_extensions.serialization.path_serialization_converter import PathSerializationConverter
from benjaminhamon_standard_extensions.serialization.serialization_converter import SerializationConverter

from benjaminhamon_sysadmin_toolkit.git.gitea_administration_configuration import GiteaAdministrationConfiguration
from benjaminhamon_sysadmin_toolkit.security.credentials_serialization_converter import CredentialsSerializationConverter


def factory() -> "GiteaAdministrationConfigurationSerializationConverter":
    return GiteaAdministrationConfigurationSerializationConverter(
        credential_converter = CredentialsSerializationConverter(),
        path_converter = PathSerializationConverter())


class GiteaAdministrationConfigurationSerializationConverter(SerializationConverter):


    def __init__(self, credential_converter: SerializationConverter, path_converter: SerializationConverter) -> None:
        self._credential_converter = credential_converter
        self._path_converter = path_converter


    def convert_from_serializable(self, obj_as_serializable: Any) -> Any:
        if obj_as_serializable is None:
            return None

        if not isinstance(obj_as_serializable, dict):
            raise ValueError("obj_as_serializable is not of the expected type")

        return GiteaAdministrationConfiguration(
            instance_path = self._path_converter.convert_from_serializable(obj_as_serializable["instance_path"]),
            service_identifier = obj_as_serializable["service_identifier"],
            database_scheme = obj_as_serializable["database_scheme"],
            database_name = obj_as_serializable["database_name"],
            database_credentials = self._credential_converter.convert_from_serializable(obj_as_serializable["database_credentials"]),
        )


    def convert_to_serializable(self, obj: Any) -> Any:
        raise NotImplementedError
