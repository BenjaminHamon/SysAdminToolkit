from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand
from benjaminhamon_standard_extensions.processes.process_options import ProcessOptions
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.services.system_service_manager_client import SystemServiceManagerClient


class LinuxServiceManagerClient(SystemServiceManagerClient):


    def __init__(self, process_runner: ProcessRunner) -> None:
        self._process_runner = process_runner
        self._systemctl_executable = "systemctl"


    async def is_service_running(self, service_identifier: str) -> bool:
        command = ExecutableCommand(self._systemctl_executable)
        command.add_arguments([ "status", service_identifier ])
        options = ProcessOptions()

        process_result = await self._process_runner.run(command, options, check_exit_code = False)

        return process_result.exit_code == 0
