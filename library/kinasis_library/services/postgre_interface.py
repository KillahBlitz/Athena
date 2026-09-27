from __future__ import annotations

import os
from abc import ABC
from types import TracebackType
from typing import Any, Mapping

from sqlalchemy import Connection, CursorResult, Engine, TextClause, create_engine, text


def create_postgres_engine(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str | None = None,
) -> Engine:
    database_suffix: str = f"/{database}" if database else ""
    url: str = f"postgresql://{user}:{password}@{host}:{port}{database_suffix}"
    return create_engine(url)


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
    def __init__(self, connection: Connection, table: str) -> None:
        self.connection: Connection = connection
        self.table: str = table

    def get_connection(self) -> Connection:
        return self.connection

    def close(self) -> None:
        if hasattr(self, "connection") and self.connection is not None and not self.connection.closed:
            self.connection.close()

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def execute_query(
        self,
        query: str | TextClause,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        statement: TextClause = text(query) if isinstance(query, str) else query
        result: CursorResult[Any] = self.connection.execute(
            statement, parameters or {}
        )
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