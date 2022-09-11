from .model import wrap_model, Model
import asyncpg


class Client:
    def __init__(self):
        self._conn_args = []
        self._conn_kwargs = {}
        self.model = wrap_model(self)
        self.models = []
        self._pool = None

    def add_model(self, model: Model):
        self.models.append(model)

    async def create_tables(self):
        async with self._pool.acquire() as connection:
            for model in self.models:
                await connection.execute(
                    f"CREATE TABLE IF NOT EXISTS "
                    f"{model.table_name} "
                    f"({', '.join([f'{name} {type.get_db_type()}' for name, type in model.get_columns().items()])})"
                )

    async def start(self, *conn_args, **conn_kwargs):
        self._conn_args = conn_args
        self._conn_kwargs = conn_kwargs
        self._pool = await asyncpg.create_pool(*self._conn_args, **self._conn_kwargs)

    async def stop(self):
        await self._pool.close()

    def get_connection(self):
        return self._pool.acquire()
