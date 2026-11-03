from __future__ import annotations

import os
from abc import ABC
from types import TracebackType
from typing import Any, Mapping

from sqlalchemy import Connection, CursorResult, Engine, TextClause, create_engine, text

DEFAULT_ENGINE_OPTIONS: dict[str, Any] = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,
    "pool_size": 5,
    "max_overflow": 5,
}

def create_postgres_engine(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str | None = None,
    **engine_options: Any,
) -> Engine:
    database_suffix: str = f"/{database}" if database else ""
    url: str = f"postgresql://{user}:{password}@{host}:{port}{database_suffix}"
    return create_engine(url, **{**DEFAULT_ENGINE_OPTIONS, **engine_options})


def create_postgres_connection(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str | None = None,
) -> Connection:
    engine: Engine = create_postgres_engine(
        port=port,
        host=host,
        password=password,
        user=user,
        database=database,
    )
    return engine.connect()


class Repository(ABC):
    def __init__(self, bind: Engine | Connection, table: str) -> None:
        self.engine: Engine | None = bind if isinstance(bind, Engine) else None
        self.connection: Connection | None = bind if isinstance(bind, Connection) else None
        self.table: str = table

    def get_connection(self) -> Connection:
        if self.connection is not None:
            return self.connection
        return self.engine.connect()

    def close(self) -> None:
        if self.connection is not None and not self.connection.closed:
            self.connection.close()

    def commit(self) -> None:
        if self.connection is not None:
            self.connection.commit()

    def rollback(self) -> None:
        if self.connection is not None:
            self.connection.rollback()

    def execute_query(
        self,
        query: str | TextClause,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        statement: TextClause = text(query) if isinstance(query, str) else query
        if self.engine is not None:
            with self.engine.begin() as connection:
                return self._rows(connection.execute(statement, parameters or {}))
        try:
            return self._rows(self.connection.execute(statement, parameters or {}))
        except Exception:
            self.connection.rollback()
            raise

    @staticmethod
    def _rows(result: CursorResult[Any]) -> list[dict[str, Any]]:
        if result.returns_rows:
            return [dict(row) for row in result.mappings().all()]
        return []

    def __enter__(self) -> Repository:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
