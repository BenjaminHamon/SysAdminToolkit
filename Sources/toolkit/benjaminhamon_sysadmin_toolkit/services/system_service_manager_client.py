import abc


class SystemServiceManagerClient(abc.ABC):
    """ Client to interact with the service manager for the local operating system """

    @abc.abstractmethod
    async def is_service_running(self, service_identifier: str) -> bool:
        pass
