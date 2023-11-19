"""System Bridge Shared: Database"""
from __future__ import annotations

import os
from collections.abc import Mapping
from time import time
from typing import Any

from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from .base import Base
from .common import convert_string_to_correct_type, get_user_data_directory
from .const import MODEL_SECRETS, MODEL_SETTINGS


class Data(SQLModel):
    """Database Data"""

    key: str = Field(primary_key=True, nullable=False)
    value: str | None = Field(default=None, nullable=True)
    timestamp: float | None = Field(default=None, nullable=True)


class Secrets(Data, table=True):
    """Database Data Secrets"""


class Settings(Data, table=True):
    """Database Data Settings"""


TABLE_MAP: Mapping[str, Any] = {
    MODEL_SECRETS: Secrets,
    MODEL_SETTINGS: Settings,
}


type TableDataType = Secrets | Settings


SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


class Database(Base):
    """Database"""

    def __init__(self):
        """Initialise"""
        super().__init__()
        self._engine = create_engine(
            f"sqlite:///{os.path.join(get_user_data_directory(), 'systembridge.db')}"
        )
        SQLModel.metadata.create_all(
            self._engine,
            # tables=TABLES,
        )

    def clear_table(
        self,
        table: Any,
    ) -> None:
        """Clear table"""
        with Session(self._engine, autoflush=True) as session:
            for sensor in session.exec(select(table)).all():
                session.delete(sensor)
            session.commit()

    def get_data(
        self,
        table: Any,
    ) -> list[Any]:
        """Get data from database"""
        with Session(self._engine, autoflush=True) as session:
            return session.exec(select(table)).all()

    def get_data_by_key(
        self,
        table: Any,
        key: str,
    ) -> list[Data]:
        """Get data from database by key"""
        with Session(self._engine, autoflush=True) as session:
            return session.exec(select(table).where(table.key == key)).all()

    def get_data_item_by_key(
        self,
        table: Any,
        key: str,
    ) -> Data | None:
        """Get data item from database by key"""
        with Session(self._engine, autoflush=True) as session:
            return session.exec(select(table).where(table.key == key)).first()

    def get_data_dict(
        self,
        table: Any,
    ) -> dict[str, Any]:
        """Get data from database as dictionary"""
        data: dict[str, Any] = {}
        data_last_updated: dict[str, float | None] = {}
        result = self.get_data(table)
        for item in result:
            if item is None or item.value is None:
                data[item.key] = None
            else:
                data[item.key] = convert_string_to_correct_type(item.value)
            if item is None or item.timestamp is None:
                data_last_updated[item.key] = None
            else:
                data_last_updated[item.key] = item.timestamp

        return {
            **data,
            "last_updated": data_last_updated,
        }

    def update_data(
        self,
        table,
        data: Any,
    ) -> None:
        """Update data"""
        with Session(self._engine, autoflush=True) as session:
            result = session.exec(select(table).where(table.key == data.key))
            if (old_data := result.first()) is None:
                data.timestamp = time()
                session.add(data)
            else:
                old_data.value = data.value
                old_data.timestamp = time()
                session.add(old_data)
            session.commit()
            if old_data is not None:
                session.refresh(old_data)
