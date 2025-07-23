from typing import Any

from benjaminhamon_standard_extensions.serialization.serialization_converter import SerializationConverter
from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


class CredentialsSerializationConverter(SerializationConverter):


    def convert_from_serializable(self, obj_as_serializable: Any) -> Any:
        if obj_as_serializable is None:
            return None

        if not isinstance(obj_as_serializable, dict):
            raise ValueError("obj_as_serializable is not of the expected type")

        return Credentials(
            username = obj_as_serializable["username"],
            secret = obj_as_serializable["secret"],
        )


    def convert_to_serializable(self, obj: Any) -> Any:
        if obj is None:
            return None

        if isinstance(obj, Credentials):
            raise ValueError("obj is not of the expected type")

        return {
            "username": obj.username,
            "secret": obj.secret,
        }
