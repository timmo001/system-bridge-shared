"""Settings."""
from __future__ import annotations

from dataclasses import asdict
from json import dumps, loads
import os
from os.path import exists
from typing import Any

from cryptography.fernet import Fernet

from systembridgemodels.settings import (
    SettingDirectory,
    SettingHotkey,
    Settings as SettingsModel,
    SettingsAPI,
    SettingsMedia,
)

from .base import Base
from .common import get_user_data_directory


class Settings(Base):
    """Settings."""

    def __init__(self) -> None:
        """Initialise."""
        super().__init__()

        # Generate default encryption key
        self._encryption_key: str = ""

        secret_key_dir: str = get_user_data_directory()

        # Create secret key directory if it doesn't exist
        if not exists(secret_key_dir):
            os.makedirs(secret_key_dir)

        secret_key_path = os.path.join(secret_key_dir, "secret.key")
        if exists(secret_key_path):
            with open(secret_key_path, encoding="utf-8") as file:
                self._encryption_key = file.read().splitlines()[0]
        if not self._encryption_key:
            self._encryption_key = Fernet.generate_key().decode()
            with open(secret_key_path, "w", encoding="utf-8") as file:
                file.write(self._encryption_key)

        # Create or read settings file
        settings: SettingsModel | None = None
        try:
            if exists(self.settings_path):
                with open(self.settings_path, encoding="utf-8") as file:
                    settings_dict = loads(file.read())
                settings = self._parse_settings(settings_dict)
        except Exception as error:  # pylint: disable=broad-except
            self._logger.error("Failed to read settings file.", exc_info=error)

        if settings is None:
            settings = SettingsModel()
            self._save(settings)

        self._settings: SettingsModel = settings

    def _parse_settings(self, settings_dict: dict[str, Any]) -> SettingsModel:
        """Parse settings."""
        return SettingsModel(
            api=SettingsAPI(**settings_dict["api"]),
            autostart=settings_dict["autostart"],
            keyboard_hotkeys=[
                SettingHotkey(**hotkey) for hotkey in settings_dict["keyboard_hotkeys"]
            ],
            log_level=settings_dict["log_level"],
            media=SettingsMedia(
                directories=[
                    SettingDirectory(**directory)
                    for directory in settings_dict["media"]["directories"]
                ]
            ),
        )

    def _save(self, settings: SettingsModel) -> None:
        """Save settings to file."""
        with open(self.settings_path, "w", encoding="utf-8") as file:
            # TODO: Encrypt settings
            file.write(dumps(asdict(settings)))

    @property
    def data(self) -> SettingsModel:
        """Return settings."""
        return self._settings

    @property
    def settings_path(self) -> str:
        """Return settings path."""
        return os.path.join(get_user_data_directory(), "settings.json")

    def update(self, settings_dict: dict[str, Any]) -> None:
        """Update settings."""
        self._settings = self._parse_settings(settings_dict)
        self._save(self._settings)
