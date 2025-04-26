import logging
import os
from typing import Dict, Optional

from benjaminhamon_standard_extensions.processes import process_helpers
from benjaminhamon_standard_extensions.processes.exceptions.process_failure_exception import ProcessFailureException
from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand
from benjaminhamon_standard_extensions.processes.process_options import ProcessOptions
from benjaminhamon_standard_extensions.processes.process_output_collector import ProcessOutputCollector
from benjaminhamon_standard_extensions.processes.process_output_logger import ProcessOutputLogger
from benjaminhamon_standard_extensions.processes.process_result import ProcessResult
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient
from benjaminhamon_sysadmin_toolkit.security.credentials import Credentials


logger = logging.getLogger("PostgreSql")


class PostgreSqlAdministrationClient(DatabaseAdministrationClient):


    def __init__(self, process_runner: ProcessRunner, database_name: str, credentials: Credentials) -> None:
        self._process_runner = process_runner

        self.scheme = "postgresql"
        self.psql_executable = "psql"
        self.pg_dump_executable = "pg_dump"

        self._database_name = database_name
        self._credentials = credentials


    def get_public_url(self) -> str:
        return "%s://***/%s" % (self.scheme, self._database_name)


    async def exists(self) -> bool:
        result = await self._run_command("\\quit")
        return result.exit_code == 0


    async def is_initialized(self) -> bool:
        result = await self._run_command("\\dt")
        if result.error_output is None:
            raise RuntimeError("Process output should not be none")
        return result.error_output.strip() == ""


    async def export(self,
            output_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        dump_file_name = "%s.dump.sql" % self._database_name
        dump_file_path = os.path.join(output_directory, dump_file_name)

        dump_command = ExecutableCommand(self.pg_dump_executable)
        dump_command.add_arguments([ "--dbname", self._database_name, "--file", dump_file_path ])

        await self._run_any(dump_command, log_file_path = log_file_path, simulate = simulate)

        logger.debug("Output file path: '%s'", dump_file_path)


    async def restore(self,
            source_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        dump_file_name = "%s.dump.sql" % self._database_name
        dump_file_path = os.path.join(source_directory, dump_file_name)

        restore_command = ExecutableCommand(self.psql_executable)
        restore_command.add_arguments([ "--dbname", self._database_name, "--file", dump_file_path, "--quiet" ])

        await self._run_any(restore_command, log_file_path = log_file_path, simulate = simulate)


    async def _run_any(self, command: ExecutableCommand, *,
            log_file_path: Optional[str] = None, simulate: bool = False) -> ProcessResult:

        if self._credentials.username is not None:
            command.add_internal_arguments([ "--username", self._credentials.username ], [ "--username", "***" ])
        if self._credentials.secret is None:
            command.add_arguments([ "--host", "localhost" ])

        process_environment: Dict[str,str] = {}
        if self._credentials.secret is not None:
            process_environment["PGPASSWORD"] = self._credentials.secret

        process_options = ProcessOptions(environment = process_environment)
        raw_logger = process_helpers.create_raw_logger(log_file_path = log_file_path)
        process_output_logger = ProcessOutputLogger(raw_logger.get_actual_logger())

        logger.debug("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        try:
            if not simulate:
                result = await self._process_runner.run(command, process_options, output_handlers = [ process_output_logger ], check_exit_code = False)
            else:
                result = ProcessResult(executable = command.executable_path, exit_code = 0)
        finally:
            if log_file_path is not None:
                logger.debug("Process log file: '%s'", log_file_path)
            raw_logger.dispose()

        self._check_exit_code(result, raise_on_error = True)

        return result


    async def _run_command(self, psql_command: str, *,
            raise_on_error: bool = True, simulate: bool = False) -> ProcessResult:

        command = ExecutableCommand(self.psql_executable)
        command.add_arguments([ "--dbname", self._database_name, "--command", psql_command ])

        if self._credentials.username is not None:
            command.add_internal_arguments([ "--username", self._credentials.username ], [ "--username", "***" ])
        if self._credentials.secret is None:
            command.add_arguments([ "--host", "localhost" ])

        process_environment: Dict[str,str] = {}
        if self._credentials.secret is not None:
            process_environment["PGPASSWORD"] = self._credentials.secret

        process_options = ProcessOptions(environment = process_environment)
        process_output_collector = ProcessOutputCollector()

        logger.debug("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        if not simulate:
            result = await self._process_runner.run(command, process_options, output_handlers = [ process_output_collector ], check_exit_code = False)
        else:
            result = ProcessResult(executable = command.executable_path, exit_code = 0)

        self._check_exit_code(result, raise_on_error = raise_on_error)

        return ProcessResult(result.executable, result.exit_code, process_output_collector.get_stdout(), process_output_collector.get_stderr())


    def _check_exit_code(self, process_result: ProcessResult, *, raise_on_error: bool = True) -> None:
        # psql returns 0 to the shell if it finished normally,
        # 1 if a fatal error of its own occurs (e.g., out of memory, file not found),
        # 2 if the connection to the server went bad and the session was not interactive,
        # and 3 if an error occurred in a script and the variable ON_ERROR_STOP was set.

        if process_result.exit_code == 0:
            return

        if process_result.exit_code == 1:
            exception_message = "Postgresql process failed with a fatal error"
            exception_message += " (Executable: '%s', ExitCode: %s)" % (process_result.executable, process_result.exit_code)
            raise ProcessFailureException(exception_message, process_result.executable, process_result.exit_code)

        if process_result.exit_code == 2:
            exception_message = "Postgresql process failed with a connection error"
            exception_message += " (Executable: '%s', ExitCode: %s)" % (process_result.executable, process_result.exit_code)
            raise ProcessFailureException(exception_message, process_result.executable, process_result.exit_code)

        if process_result.exit_code == 3:
            if not raise_on_error:
                return
            exception_message = "Postgresql process failed with a script error"
            exception_message += " (Executable: '%s', ExitCode: %s)" % (process_result.executable, process_result.exit_code)
            raise ProcessFailureException(exception_message, process_result.executable, process_result.exit_code)

        raise RuntimeError("Unexpected postgresql process exit code: %s" % process_result.exit_code)
