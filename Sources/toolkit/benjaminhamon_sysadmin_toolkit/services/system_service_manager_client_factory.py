import platform

from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner
from benjaminhamon_standard_extensions.processes.process_spawner import ProcessSpawner

from benjaminhamon_sysadmin_toolkit.services.linux_service_manager_client import LinuxServiceManagerClient
from benjaminhamon_sysadmin_toolkit.services.system_service_manager_client import SystemServiceManagerClient


def create_service_manager() -> SystemServiceManagerClient:
    if platform.system() == "Linux":
        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        return LinuxServiceManagerClient(process_runner)

    raise ValueError("System is not supported: '%s'" % platform.system())
