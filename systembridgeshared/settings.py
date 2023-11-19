"""System Bridge: Settings"""
from __future__ import annotations

import os
from dataclasses import asdict
from json import dumps, loads
from os.path import exists
from typing import Any

from appdirs import AppDirs
from cryptography.fernet import Fernet
from systembridgemodels.settings import Settings as SettingsModel

from .base import Base


class Settings(Base):
    """Settings"""

    def __init__(self) -> None:
        """Initialise"""
        super().__init__()

        # Generate default encryption key
        self._encryption_key: str = ""
        secret_key_path = os.path.join(
            AppDirs("systembridge", "timmo001").user_data_dir, "secret.key"
        )
        if exists(secret_key_path):
            with open(secret_key_path, encoding="utf-8") as file:
                self._encryption_key = file.read().splitlines()[0]
        if not self._encryption_key:
            self._encryption_key = Fernet.generate_key().decode()
            with open(secret_key_path, "w", encoding="utf-8") as file:
                file.write(self._encryption_key)

        # Create or read settings file
        if exists(self.settings_path):
            with open(self.settings_path, encoding="utf-8") as file:
                self._settings = SettingsModel(loads(file.read()))
        if not self._settings:
            self._settings = SettingsModel()
            self._save()

    def _save(self) -> None:
        """Save settings to file"""
        with open(self.settings_path, "w", encoding="utf-8") as file:
            file.write(dumps(asdict(self._settings)))

    @property
    def data(self) -> SettingsModel:
        """Return settings"""
        return self._settings

    @property
    def settings_path(self) -> str:
        """Return settings path"""
        return os.path.join(
            AppDirs("systembridge", "timmo001").user_data_dir, "settings.json"
        )

    def update(self, key: str, value: Any) -> None:
        """Update setting"""
        setattr(self._settings, key, value)
        self._save()
