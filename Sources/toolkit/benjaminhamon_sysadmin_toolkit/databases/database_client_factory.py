from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner
from benjaminhamon_standard_extensions.processes.process_spawner import ProcessSpawner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient
from benjaminhamon_sysadmin_toolkit.databases.mongodb_administration_client import MongoDbAdministrationClient
from benjaminhamon_sysadmin_toolkit.databases.mysql_administration_client import MySqlAdministrationClient
from benjaminhamon_sysadmin_toolkit.databases.postgresql_administration_client import PostgreSqlAdministrationClient
from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


def create_administration_client(database_scheme: str, database_name: str, credentials: Credentials) -> DatabaseAdministrationClient:
    if database_scheme == "mongodb":
        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        return MongoDbAdministrationClient(process_runner, database_name, credentials)
    if database_scheme == "mysql":
        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        return MySqlAdministrationClient(process_runner, database_name, credentials)
    if database_scheme == "postgresql":
        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        return PostgreSqlAdministrationClient(process_runner, database_name, credentials)

    raise ValueError("Database scheme is not supported: '%s'" % database_scheme)
