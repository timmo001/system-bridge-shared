"""System Bridge: Models - Database Data Sensors"""

from __future__ import annotations

from sqlmodel import Field

from .database_data import Data


class Sensors(Data, table=True):
    """Database Data Sensors"""

    type: str = Field(nullable=False)
    name: str | None = Field(default=None, nullable=True)
    hardware_type: str | None = Field(default=None, nullable=True)
    hardware_name: str | None = Field(default=None, nullable=True)
