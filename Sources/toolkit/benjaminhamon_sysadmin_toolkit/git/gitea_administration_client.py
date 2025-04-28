import glob
import logging
import os
import shutil
from typing import List, Tuple

from benjaminhamon_standard_extensions.archives.archive_operations import ArchiveOperations
from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner

from benjaminhamon_sysadmin_toolkit.databases.database_administration_client import DatabaseAdministrationClient
from benjaminhamon_sysadmin_toolkit.services.system_service_manager_client import SystemServiceManagerClient


logger = logging.getLogger("Gitea")


class GiteaAdministrationClient:


    def __init__(self, # pylint: disable = too-many-arguments, too-many-positional-arguments
            process_runner: ProcessRunner,
            database_administration_client: DatabaseAdministrationClient,
            archive_operations: ArchiveOperations,
            service_manager_client: SystemServiceManagerClient,
            instance_path: str,
            service_identifier: str) -> None:

        self._process_runner = process_runner
        self._database_administration_client = database_administration_client
        self._archive_operations = archive_operations
        self._service_manager_client = service_manager_client
        self._service_identifier = service_identifier
        self._instance_path = instance_path


    async def is_service_running(self) -> bool:
        return await self._service_manager_client.is_service_running(self._service_identifier)


    async def backup(self,
            archive_file_path: str, intermediate_directory: str, *,
            check_not_running: bool = True, simulate: bool = False) -> None:

        logger.info("Backing up Gitea (Path: '%s')", self._instance_path)

        if check_not_running:
            if await self.is_service_running():
                raise RuntimeError("Gitea service should not be running")

        database_dump_directory = os.path.join(intermediate_directory, "database")
        database_backup_log_file_path = os.path.join(database_dump_directory, "database_backup.log")
        data_source_directory = os.path.join(self._instance_path, "data")
        data_copy_directory = os.path.join(intermediate_directory, "data")

        if not os.path.exists(data_source_directory):
            raise RuntimeError("Gitea data directory does not exist (Path: '%s')" % data_source_directory)
        if not await self._database_administration_client.exists():
            raise RuntimeError("Gitea database does not exist (URL: '%s')" % self._database_administration_client.get_public_url())

        if not simulate:
            if os.path.exists(intermediate_directory):
                shutil.rmtree(intermediate_directory)
            os.makedirs(intermediate_directory, mode = 0o700)

        try:
            logger.info("Dumping database ('%s' => '%s')", self._database_administration_client.get_public_url(), database_dump_directory)
            await self._database_administration_client.export(
                database_dump_directory, log_file_path = database_backup_log_file_path, simulate = simulate)

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


    async def restore(self,
            archive_file_path: str, intermediate_directory: str, *,
            check_not_running: bool = True, simulate: bool = False) -> None:

        logger.info("Restoring Gitea (Path: '%s')", self._instance_path)

        if check_not_running:
            if await self.is_service_running():
                raise RuntimeError("Gitea service should not be running")

        database_dump_directory = os.path.join(intermediate_directory, "database")
        database_restore_log_file_path = os.path.join(intermediate_directory, "database_restore.log")
        data_actual_directory = os.path.join(self._instance_path, "data")
        data_intermediate_directory = os.path.join(intermediate_directory, "data")

        if os.path.exists(data_actual_directory):
            raise RuntimeError("Gitea data directory already exists (Path: '%s')" % data_actual_directory)
        if not await self._database_administration_client.exists():
            raise RuntimeError("Gitea database does not exist (URL: '%s')" % self._database_administration_client.get_public_url())
        if await self._database_administration_client.is_initialized():
            raise RuntimeError("Gitea database is already initialized (URL: '%s')" % self._database_administration_client.get_public_url())

        if not simulate:
            if os.path.exists(intermediate_directory):
                shutil.rmtree(intermediate_directory)
            os.makedirs(intermediate_directory, mode = 0o700)

        try:
            logger.info("Extracting archive (FilePath: '%s')", archive_file_path)
            self._archive_operations.extract(archive_file_path, intermediate_directory, simulate = simulate)

            logger.info("Moving data files ('%s' => '%s')", data_intermediate_directory, data_actual_directory)
            if not simulate:
                shutil.move(data_intermediate_directory, data_actual_directory + ".tmp")
                os.rename(data_actual_directory + ".tmp", data_actual_directory)

            logger.info("Restoring database ('%s' => '%s')", database_dump_directory, self._database_administration_client.get_public_url())
            await self._database_administration_client.restore(
                database_dump_directory, log_file_path = database_restore_log_file_path, simulate = simulate)

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
