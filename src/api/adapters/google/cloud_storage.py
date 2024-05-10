"""Module with the implementation of cloud storage."""

import asyncio
import datetime
import functools
import os

from google.cloud import storage  # type: ignore[attr-defined]
from google.oauth2 import service_account

from api import ports


class CloudStorage(ports.Storage):
    """Implementation of google's cloud storage."""

    def __init__(self, project_id: str, storage_path: str, creds_path: str):
        credentials = None
        if creds_path:
            credentials = service_account.Credentials.from_service_account_file(
                creds_path
            )
        self.client = storage.Client(project=project_id, credentials=credentials)
        self.storage_path = storage_path
        self.file_path = "/tmp"

    async def download(self, uri: str, file_name: str) -> str:
        """Download file from GCS."""
        file_gcs_path = uri
        path_tmp = f"{self.file_path}/{file_name}"
        await asyncio.to_thread(
            functools.partial(self._download_sync, file_gcs_path, path_tmp)
        )
        return path_tmp

    def _download_sync(self, gcs_path: str, path_tmp: str) -> None:
        """Download file from GCS."""
        with open(path_tmp, "wb") as file:
            self.client.download_blob_to_file(gcs_path, file)

    async def upload_by_text(self, path: str, text: bytes, content_type: str) -> str:
        """Upload file to GCS by text."""
        blob = self.client.bucket(self.storage_path).blob(path)
        await asyncio.to_thread(
            functools.partial(blob.upload_from_string, text, content_type=content_type)
        )
        return str(blob.id.rsplit("/", 1)[0])

    async def upload_by_file(self, path: str, file_path: str) -> str:
        """Upload file to GCS by file."""
        blob = self.client.bucket(self.storage_path).blob(path)
        await asyncio.to_thread(functools.partial(blob.upload_from_filename, file_path))
        blob_id: str = blob.id
        end_path: str = blob_id.rsplit("/", 1)[0]
        os.remove(file_path)
        return end_path

    async def generate_signed_url(
        self, path: str, mimetype: str, method: str = "PUT"
    ) -> str:
        blob = self.client.bucket(self.storage_path).blob(path)
        response: str = await asyncio.to_thread(
            functools.partial(
                blob.generate_signed_url,
                method=method,
                expiration=datetime.timedelta(hours=1),
                version="v4",
                content_type=mimetype if method != "GET" else None,
            )
        )
        return response
