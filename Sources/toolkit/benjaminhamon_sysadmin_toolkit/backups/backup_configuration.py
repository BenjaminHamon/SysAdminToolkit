# cspell:words gitea levelname

import dataclasses

from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


@dataclasses.dataclass
class BackupConfiguration:
    identifier: str

    local_archive_directory: str
    archive_name_format: str
    archive_date_format: str

    repository_service_url: str
    repository: str
    repository_credentials: Credentials
