import abc
from typing import Optional


class DatabaseAdministrationClient(abc.ABC):


    @abc.abstractmethod
    def get_public_url(self) -> str:
        pass


    @abc.abstractmethod
    async def export_database(self,
            output_directory: str, *, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        pass
