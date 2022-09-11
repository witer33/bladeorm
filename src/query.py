from .utils import Operator, ValuesManager
from abc import ABC, abstractmethod
from typing import Dict, Union, Any, TYPE_CHECKING, List

if TYPE_CHECKING:
    from .model import Model


class QueryExecutor(ABC):
    @abstractmethod
    async def fetch(
        self, *results: Union[Operator, Any], limit: int = None, offset: int = None
    ) -> List["Model"]:
        pass

    @abstractmethod
    async def fetchone(self, *results: Union[Operator, Any]) -> "Model":
        pass

    @abstractmethod
    async def update(self, **values: Dict[str, Union[Operator, Any]]):
        pass

    @abstractmethod
    async def delete(self):
        pass


class ModelExecutor(QueryExecutor):
    def __init__(self, model: "Model", where: Operator = None):
        self._model = model
        self._where = where

    def filter(self, where: Operator) -> QueryExecutor:
        return ModelExecutor(self._model, where)

    def __call__(self, *args, **kwargs):
        return self.filter(*args, **kwargs)

    async def fetch(
        self, *results: Union[Operator, Any], limit: int = None, offset: int = None
    ) -> List["Model"]:
        async with self._model.get_client().get_connection() as connection:
            manager: ValuesManager = ValuesManager()
            results_data = [
                result.build(manager) if isinstance(result, Operator) else result
                for result in results
            ]
            query = (
                f"SELECT "
                f"{','.join(results_data) if results_data else '*'} "
                f"FROM {self._model.table_name} "
                f"{'WHERE ' + self._where.build(manager) if self._where else ''} "
                f"{'LIMIT ' + manager.add(limit) if limit else ''} "
                f"{'OFFSET ' + manager.add(offset) if offset else ''}"
            )

            rows = await connection.fetch(query, *manager.get_storage())
            return [self._model.create_instance(dict(row), True) for row in rows]

    async def fetchone(self, *results: Union[Operator, Any]) -> "Model":
        async with self._model.get_client().get_connection() as connection:
            manager: ValuesManager = ValuesManager()
            results_data = [
                result.build(manager) if isinstance(result, Operator) else result
                for result in results
            ]
            query = (
                f"SELECT "
                f"{','.join(results_data) if results_data else '*'} "
                f"FROM {self._model.table_name} "
                f"{'WHERE ' + self._where.build(manager) if self._where else ''} "
                f"LIMIT 1"
            )

            row = await connection.fetchrow(query, *manager.get_storage())
            return self._model.create_instance(dict(row), True) if row else None

    async def update(self, **values: Dict[str, Union[Operator, Any]]):
        async with self._model.get_client().get_connection() as connection:
            manager: ValuesManager = ValuesManager()
            query = (
                f"UPDATE {self._model.table_name} "
                f"SET {','.join([f'{key}={value.build(manager) if isinstance(value, Operator) else manager.add(value)}' for key, value in values.items()])} "
                f"{'WHERE ' + self._where.build(manager) if self._where else ''}"
            )

            await connection.execute(query, *manager.get_storage())

    async def delete(self):
        async with self._model.get_client().get_connection() as connection:
            manager: ValuesManager = ValuesManager()
            query = (
                f"DELETE FROM {self._model.table_name} "
                f"{'WHERE ' + self._where.build(manager) if self._where else ''}"
            )

            await connection.execute(query, *manager.get_storage())

    async def insert(self, model: "Model"):
        async with self._model.get_client().get_connection() as connection:
            manager: ValuesManager = ValuesManager()
            columns = []
            values = []
            for column, value in model.get_values().items():
                columns.append(column)
                values.append(manager.add(value))

            query = (
                f"INSERT INTO {self._model.table_name} "
                f"({','.join(columns)}) "
                f"VALUES ({','.join(values)})"
            )
            await connection.execute(query, *manager.get_storage())
