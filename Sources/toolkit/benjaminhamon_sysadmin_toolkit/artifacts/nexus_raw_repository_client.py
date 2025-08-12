import logging
import os
from typing import List, Optional

from benjaminhamon_standard_extensions.web.form_data import FormData
from benjaminhamon_standard_extensions.web.form_data_field import FormDataField
from benjaminhamon_standard_extensions.web.web_api_client_async import WebApiClientAsync
from benjaminhamon_standard_extensions.web.web_client_async import WebClientAsync
from benjaminhamon_standard_extensions.web.web_content_exception import WebContentException


logger = logging.getLogger("Nexus")


class NexusRawRepositoryClient:


    def __init__(self, service_url: str, web_client: WebApiClientAsync, web_client_for_download: Optional[WebClientAsync] = None) -> None:
        self._service_url = service_url
        self._web_client = web_client
        self._web_client_for_download = web_client_for_download

        self._web_client.default_response_success_obj_type = None
        self._web_client.default_response_error_obj_type = list


    async def list_artifacts(self, repository: str) -> List[dict]:
        method = "GET"
        endpoint = self._service_url + "/components"
        parameters = { "repository": repository }

        response = await self._web_client.send_request(method, endpoint, parameters = parameters, response_success_obj_type = dict)

        if response.data is None:
            raise WebContentException(response.request_identifier, method, endpoint, response.status_code, response)

        item_collection: List[dict] = response.data["items"]
        artifact_collection: List[dict] = []

        for item in item_collection:
            artifact_collection.append({
                "internal_identifier": item["id"],
                "path": item["name"],
            })

        return artifact_collection


    async def list_artifacts_from_group(self, repository: str, group: str) -> List[dict]:
        method = "GET"
        endpoint = self._service_url + "/search"
        parameters = { "repository": repository, "group": "/" + group }

        response = await self._web_client.send_request(method, endpoint, parameters = parameters, response_success_obj_type = dict)

        if response.data is None:
            raise WebContentException(response.request_identifier, method, endpoint, response.status_code, response)

        item_collection: List[dict] = response.data["items"]
        artifact_collection: List[dict] = []

        for item in item_collection:
            artifact_collection.append({
                "internal_identifier": item["id"],
                "path": item["name"],
            })

        return artifact_collection


    async def get_artifact_by_path(self, repository: str, path: str) -> Optional[dict]:
        method = "GET"
        endpoint = self._service_url + "/search"
        parameters = { "repository": repository, "name": "/" + path }

        response = await self._web_client.send_request(method, endpoint, parameters = parameters, response_success_obj_type = dict)

        if response.data is None:
            raise WebContentException(response.request_identifier, method, endpoint, response.status_code, response)

        item_collection: List[dict] = response.data["items"]
        if len(item_collection) == 0:
            return None

        return {
            "internal_identifier": item_collection[0]["id"],
            "path": item_collection[0]["name"],
        }


    async def download_artifact(self, repository: str, remote_file_path: str, local_file_path: str, *, simulate: bool = False) -> None:
        if self._web_client_for_download is None:
            raise ValueError("Web client for download was not provided")

        method = "GET"
        endpoint = self._service_url + "/search"
        parameters = { "repository": repository, "name": "/" + remote_file_path }

        response = await self._web_client.send_request(method, endpoint, parameters = parameters, response_success_obj_type = dict)

        if response.data is None:
            raise WebContentException(response.request_identifier, method, endpoint, response.status_code, response)

        item_collection: List[dict] = response.data["items"]
        if len(item_collection) == 0:
            raise WebContentException(response.request_identifier, method, endpoint, response.status_code, response)

        download_url = item_collection[0]["assets"][0]["downloadUrl"]

        await self._web_client_for_download.download(download_url, local_file_path, simulate = simulate)


    async def upload_artifact(self, repository: str, remote_file_path: str, local_file_path: str, *, simulate: bool = False) -> None:
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


    async def delete_artifact(self, identifier: str, *, simulate: bool = False) -> None:
        method = "DELETE"
        endpoint = self._service_url + "/components/" + identifier

        await self._web_client.send_request(method, endpoint, simulate = simulate)
