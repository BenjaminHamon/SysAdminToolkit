from typing import Any

from benjaminhamon_standard_extensions.serialization.path_serialization_converter import PathSerializationConverter
from benjaminhamon_standard_extensions.serialization.serialization_converter import SerializationConverter

from benjaminhamon_sysadmin_toolkit.backups.backup_configuration import BackupConfiguration
from benjaminhamon_sysadmin_toolkit.security.credentials_serialization_converter import CredentialsSerializationConverter


def factory() -> "BackupConfigurationSerializationConverter":
    return BackupConfigurationSerializationConverter(
        credential_converter = CredentialsSerializationConverter(),
        path_converter = PathSerializationConverter())


class BackupConfigurationSerializationConverter(SerializationConverter):


    def __init__(self, credential_converter: SerializationConverter, path_converter: SerializationConverter) -> None:
        self._credential_converter = credential_converter
        self._path_converter = path_converter


    def convert_from_serializable(self, obj_as_serializable: Any) -> Any:
        if obj_as_serializable is None:
            return None

        if not isinstance(obj_as_serializable, dict):
            raise ValueError("obj_as_serializable is not of the expected type")

        return BackupConfiguration(
            identifier = obj_as_serializable["identifier"],
            local_archive_directory = self._path_converter.convert_from_serializable(obj_as_serializable["local_archive_directory"]),
            archive_name_format = obj_as_serializable["archive_name_format"],
            archive_date_format = obj_as_serializable["archive_date_format"],
            repository_service_url = obj_as_serializable["repository_service_url"],
            repository = obj_as_serializable["repository"],
            repository_credentials = self._credential_converter.convert_from_serializable(obj_as_serializable["repository_credentials"]),
        )


    def convert_to_serializable(self, obj: Any) -> Any:
        raise NotImplementedError
