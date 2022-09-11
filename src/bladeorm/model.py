from .utils import DatabaseType
from .query import ModelExecutor
from typing import Dict, Any, Union, TYPE_CHECKING, List
from dataclasses import dataclass, fields
from typing import Callable
import json

if TYPE_CHECKING:
    from .client import Client

# Database types

Text = DatabaseType(str, "TEXT")
Varchar = DatabaseType(str, "VARCHAR")
Int = DatabaseType(int, "INTEGER")
Float = DatabaseType(float, "DOUBLE PRECISION")
Bool = DatabaseType(bool, "BOOLEAN")
Serial = DatabaseType(int, "SERIAL", True)


class Model(ModelExecutor):
    """
    This class wraps models and models instances.
    """

    _client = None
    _table_name = None

    def __init__(
        self,
        columns: Dict[str, DatabaseType],
        id_column: DatabaseType = None,
        original_object: "Model" = None,
        values: Dict[str, Any] = None,
        saved: bool = False,
    ):
        super().__init__(self)

        # model variables
        self._columns: Dict[str, DatabaseType] = columns
        self._id: DatabaseType = id_column

        # model instance variables
        self._original_object: Model = original_object
        self._values: Dict[str, Any] = values
        self._saved: bool = saved

        self._updated_columns: Dict[str, bool] = {}
        self._original_id = None

        if self._values and self._id:
            self._update_original_id()

        if not self._id:
            for name, column in self._columns.items():
                if column.id_status:
                    if not self._id:
                        self._id = column
                    else:
                        raise TypeError("More than one id column")

    def __getattr__(self, item):
        if not self._values:
            return self._columns[item]
        else:
            return self._values[item]

    def _update_original_id(self):
        self._original_id = self._values[self._id.get_name()]

    def _id_check(self):
        if not self._id:
            raise TypeError(f"{self.__class__.__name__} has no id column")

    def create_instance(self, values: Dict[str, Any], saved: bool = False):
        return self.__class__(self._columns, self._id, self, values, saved)

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            return self.filter(*args, **kwargs)

        return self.create_instance(kwargs)

    async def delete(self):
        if not self._original_object:
            return await super().delete()

        if not self._saved:
            raise ValueError(f"{self.__class__.__name__} not inserted")

        self._id_check()

        await self._original_object.filter(
            self._id == self._original_id
        ).delete()

    async def save(self):
        if not self._saved:
            return await self._original_object.insert(self)

        self._id_check()

        if self._updated_columns:
            result = await self._original_object.filter(
                self._id == self._original_id
            ).update(**{k: v for k, v in self._values.items() if self._updated_columns.get(k)})
            self._updated_columns = {}
            self._update_original_id()
            return result

    def __setattr__(self, key, value):
        if key.startswith("_") or key not in self._columns:
            self.__dict__[key] = value
            return

        if not self._values:
            raise TypeError(f"Model {self.__class__.__name__} is not an instance")

        self._values[key] = value
        self._updated_columns[key] = True

    def get_columns(self):
        return self._columns

    def get_client(self):
        return self._client

    def get_values(self):
        return self._values

    def get_json(self):
        return json.dumps(self._values)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._values}>"

    def __str__(self):
        return self.__repr__()

    @property
    def table_name(self):
        return self._table_name


def wrap_model(client: "Client") -> Callable[[Any], Model]:
    def model(model_class: Any) -> Model:
        """
        Creates a model from a class.
        :param model_class:
        :return Model:
        """

        table_name = f"{model_class.__name__.lower()}s"
        columns = {}

        for field in fields(dataclass(model_class)):
            if isinstance(field.type, DatabaseType):
                field.type = field.type.initialize(table_name, field.name)
                columns[field.name] = field.type

        class ModelWrapper(Model):
            _client = client
            _table_name = table_name

        ModelWrapper.__name__ = model_class.__name__
        ModelWrapper.__qualname__ = model_class.__qualname__

        result = ModelWrapper(columns)
        client.add_model(result)
        return result

    return model
