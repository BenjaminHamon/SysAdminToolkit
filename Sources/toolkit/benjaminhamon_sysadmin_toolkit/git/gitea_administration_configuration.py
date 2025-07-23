# cspell:words gitea

import dataclasses

from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


@dataclasses.dataclass
class GiteaAdministrationConfiguration:
    instance_path: str
    service_identifier: str

    database_scheme: str
    database_name: str
    database_credentials: Credentials
