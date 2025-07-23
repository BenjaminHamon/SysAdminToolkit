# cspell:words mongodump

import logging
import sys
from typing import Optional

from benjaminhamon_standard_extensions.processes import process_helpers
from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand
from benjaminhamon_standard_extensions.processes.process_options import ProcessOptions
from benjaminhamon_standard_extensions.processes.process_output_logger import ProcessOutputLogger
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient
from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


logger = logging.getLogger("MongoDB")


class MongoDbAdministrationClient(DatabaseAdministrationClient):


    def __init__(self, process_runner: ProcessRunner, database_name: str, credentials: Credentials) -> None:
        self._process_runner = process_runner

        self.scheme = "mongodb"
        self.mongodump_executable = "mongodump"

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

        dump_command = ExecutableCommand(self.mongodump_executable)
        dump_command.add_arguments([ "--db", self._database_name, "--out", output_directory ])

        if self._credentials.username is not None:
            dump_command.add_internal_arguments([ "--username", self._credentials.username ], [ "--username", "***" ])
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

        logger.debug("Output directory: '%s'", output_directory)


    async def restore(self, source_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:
        raise NotImplementedError
