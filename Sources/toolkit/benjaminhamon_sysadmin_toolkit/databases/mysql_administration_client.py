import logging
import os
import sys
from typing import Optional

from benjaminhamon_standard_extensions.processes import process_helpers
from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand
from benjaminhamon_standard_extensions.processes.process_options import ProcessOptions
from benjaminhamon_standard_extensions.processes.process_output_logger import ProcessOutputLogger
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient
from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


logger = logging.getLogger("MySql")


class MySqlAdministrationClient(DatabaseAdministrationClient):


    def __init__(self, process_runner: ProcessRunner, database_name: str, credentials: Credentials) -> None:
        self._process_runner = process_runner

        self.scheme = "mongodb"
        self.mysql_dump_executable = "mysqldump"

        self._database_name = database_name
        self._credentials = credentials


    def get_public_url(self) -> str:
        return "%s://***/%s" % (self.scheme, self._database_name)


    async def exists(self) -> bool:
        raise NotImplementedError


    async def is_initialized(self) -> bool:
        raise NotImplementedError


    async def export(self,
            output_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        dump_file_name = "%s.dump.sql" % self._database_name
        dump_file_path = os.path.join(output_directory, dump_file_name)

        dump_command = ExecutableCommand(self.mysql_dump_executable)
        dump_command.add_arguments([ self._database_name, "--result-file", dump_file_path , "--single-transaction" ])

        if self._credentials.username is not None:
            dump_command.add_internal_arguments([ "--user", self._credentials.username ], [ "--user", "***" ])
        if self._credentials.secret is not None:
            dump_command.add_internal_arguments([ "--password", self._credentials.secret ], [ "--password", "***" ])

        process_options = ProcessOptions()
        raw_logger = process_helpers.create_raw_logger(stream = sys.stdout, log_file_path = log_file_path)
        process_output_logger = ProcessOutputLogger(raw_logger.get_actual_logger())

        logger.debug("+ %s", process_helpers.format_executable_command(dump_command.get_command_for_logging()))

        try:
            if not simulate:
                await self._process_runner.run(dump_command, process_options, output_handlers = [ process_output_logger ], check_exit_code = True)
        finally:
            if log_file_path is not None:
                logger.debug("Process log file: '%s'", log_file_path)
            raw_logger.dispose()

        logger.debug("Output file path: '%s'", dump_file_path)


    async def restore(self, source_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:
        raise NotImplementedError
