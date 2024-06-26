"""Module containing storage abstract."""

import abc


class Storage(abc.ABC):
    """Storage abstract."""

    @abc.abstractmethod
    async def upload_by_file(self, path: str, audio_path: str) -> str:
        """Method that uploads a file by name."""

    @abc.abstractmethod
    async def upload_by_text(self, path: str, text: bytes, content_type: str) -> str:
        """Method that uploads a file by bytes."""

    @abc.abstractmethod
    async def download(self, uri: str, file_name: str) -> str:
        """Method that downloads a file."""

    @abc.abstractmethod
    async def generate_signed_url(
        self, path: str, mimetype: str, method: str = "PUT"
    ) -> str:
        """Method to generate a signed url."""
