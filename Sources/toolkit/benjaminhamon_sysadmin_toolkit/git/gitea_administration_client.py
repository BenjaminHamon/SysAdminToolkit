import glob
import logging
import os
import platform
import shutil
from typing import List, Tuple

from benjaminhamon_standard_extensions.archives.archive_operations import ArchiveOperations
from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand
from benjaminhamon_standard_extensions.processes.process_options import ProcessOptions
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient


logger = logging.getLogger("Gitea")


class GiteaAdministrationClient:


    def __init__(self, # pylint: disable = too-many-arguments, too-many-positional-arguments
            process_runner: ProcessRunner,
            database_administration_client: DatabaseAdministrationClient,
            archive_operations: ArchiveOperations,
            instance_path: str,
            service_name: str) -> None:

        self._process_runner = process_runner
        self._database_administration_client = database_administration_client
        self._archive_operations = archive_operations
        self._service_name = service_name
        self._instance_path = instance_path


    async def is_service_running(self) -> bool:
        if platform.system() != "Linux":
            raise NotImplementedError()

        command = ExecutableCommand("systemctl")
        command.add_arguments([ "status", self._service_name ])
        options = ProcessOptions()

        process_result = await self._process_runner.run(command, options, check_exit_code = False)

        return process_result.exit_code == 0


    async def backup(self,
            archive_file_path: str, intermediate_directory: str, *,
            check_not_running: bool = True, simulate: bool = False) -> None:

        logger.info("Backing up Gitea (Path: '%s')", self._instance_path)

        if check_not_running:
            if await self.is_service_running():
                raise RuntimeError("Gitea service should not be running")

        if not simulate:
            if os.path.exists(intermediate_directory):
                shutil.rmtree(intermediate_directory)
            os.makedirs(intermediate_directory, mode = 0o700)

        database_dump_directory = os.path.join(intermediate_directory, "database")
        database_dump_log_file_path = os.path.join(database_dump_directory, "database.dump.sql")
        data_source_directory = os.path.join(self._instance_path, "data")
        data_copy_directory = os.path.join(intermediate_directory, "data")

        try:
            logger.info("Dumping database ('%s' => '%s')", self._database_administration_client.get_public_url(), database_dump_directory)
            await self._database_administration_client.export_database(
                database_dump_directory, log_file_path = database_dump_log_file_path, simulate = simulate)

            logger.info("Copying data files ('%s' => '%s')", data_source_directory, data_copy_directory)
            if not simulate:
                shutil.copytree(data_source_directory, data_copy_directory)

            logger.info("Creating archive (FilePath: '%s')", archive_file_path)
            mapping_collection = self._map_files_for_archive(intermediate_directory)
            self._archive_operations.create(archive_file_path, mapping_collection, simulate = simulate)

        finally:
            if not simulate:
                if os.path.exists(intermediate_directory):
                    shutil.rmtree(intermediate_directory)


    def _map_files_for_archive(self, directory: str) -> List[Tuple[str,str]]:
        mapping_collection = []
        source_collection = glob.glob(os.path.join(os.path.normpath(directory), "**"), recursive = True)
        source_collection = [ file_path for file_path in source_collection if os.path.isfile(file_path) ]

        for source in source_collection:
            destination = os.path.relpath(source, directory)
            mapping_collection.append((source, destination.replace("\\", "/")))

        mapping_collection.sort()

        return mapping_collection
