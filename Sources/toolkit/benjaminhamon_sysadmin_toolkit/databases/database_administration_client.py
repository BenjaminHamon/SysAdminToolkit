import abc
from typing import Optional


class DatabaseAdministrationClient(abc.ABC):


    @abc.abstractmethod
    def get_public_url(self) -> str:
        pass


    @abc.abstractmethod
    async def exists(self) -> bool:
        pass


    @abc.abstractmethod
    async def is_initialized(self) -> bool:
        pass


    @abc.abstractmethod
    async def export(self, output_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:
        pass


    @abc.abstractmethod
    async def restore(self, source_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:
        pass
