"""Module containing all modules to be instantiated."""

import logging
import os

import injector

from . import ports
from .adapters import google, sendgrid
from .typings import Settings

logger = logging.getLogger(__name__)


class SettingsModule(injector.Module):
    """Module to contain just settings."""

    @injector.multiprovider
    @injector.singleton
    def provide_settings(self) -> Settings:
        """Provide settings from environment."""
        settings = {
            k[1:].lower(): v for k, v in os.environ.items() if k.startswith("_")
        }

        return Settings(settings)


class GoogleModule(injector.Module):
    """Google module."""

    @injector.provider
    @injector.singleton
    def provide_cloud_storage(self, settings: Settings) -> ports.Storage:
        """
        Provide the Cloud Storage.
        """
        return google.CloudStorage(
            project_id=settings.get("project_id", ""),
            storage_path=settings.get("bucket_path", ""),
            creds_path=settings.get("credentials", ""),
        )

    @injector.provider
    @injector.singleton
    def provide_pubsub(self, settings: Settings) -> ports.MessagePublisher:
        """
        Provide the GCP's Pubsub.
        """
        return google.MessagePublisher(
            project_id=settings.get("project_id", ""),
            creds_path=settings.get("gcp_bucket_credentials", ""),
            topic=settings.get("pubsub_topic", ""),
        )


class UtilModule(injector.Module):
    """
    Module for util packages.
    """

    @injector.provider
    @injector.singleton
    def provide_notification_handler(self, settings: Settings) -> ports.Notification:
        """
        Provides the sendgrid notification handler.
        """
        return sendgrid.Sendgrid(
            api_key=settings.get("sendgrid_key", ""),
            sender_email=settings.get("sender_email", ""),
        )


def create_container(mods: tuple[injector.Module] | None = None) -> injector.Injector:
    """
    Create the dependency injection container.

    :return: configured dependency injection container.
    """
    modules = mods or (
        GoogleModule(),
        SettingsModule(),
        UtilModule(),
    )

    return injector.Injector(modules)
