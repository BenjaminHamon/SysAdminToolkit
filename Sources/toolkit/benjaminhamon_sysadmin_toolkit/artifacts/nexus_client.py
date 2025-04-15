import logging
import os

from benjaminhamon_standard_extensions.web.form_data import FormData
from benjaminhamon_standard_extensions.web.form_data_field import FormDataField
from benjaminhamon_standard_extensions.web.web_api_client_async import WebApiClientAsync


logger = logging.getLogger("Nexus")


class NexusClient:


    def __init__(self, service_url: str, web_client: WebApiClientAsync) -> None:
        self._service_url = service_url
        self._web_client = web_client

        self._web_client.default_response_success_obj_type = dict
        self._web_client.default_response_error_obj_type = list


    async def upload(self, repository: str, remote_file_path: str, local_file_path: str, *, simulate: bool = False) -> None:
        endpoint = self._service_url + "/components"
        parameters = { "repository": repository }

        with open(local_file_path, mode = "rb") as local_file:
            data = FormData([
                FormDataField("raw.directory", os.path.dirname(remote_file_path)),
                FormDataField("raw.asset1", local_file),
                FormDataField("raw.asset1.filename", os.path.basename(remote_file_path)),
            ])

            logger.info("Uploading '%s' to repository '%s'", remote_file_path, repository)
            logger.debug("%s => %s", local_file_path, endpoint)

            await self._web_client.send_request("POST", endpoint, parameters = parameters, data_as_form = data, simulate = simulate)
