from typing import Any, Type, Union, List, Tuple, Callable


class ValuesManager:
    def __init__(self):
        self._storage = []

    def add(self, value: Any) -> str:
        self._storage.append(value)
        return f"${len(self._storage)}"

    def get_storage(self):
        return self._storage


class Operator:
    def __init__(
        self,
        first: Any,
        operator: str,
        second: Any,
        parenthesis: bool = False,
        no_first: bool = False,
    ):
        self.first = first
        self.operator = operator
        self.second = second
        self.parenthesis = parenthesis
        self.no_first = no_first

    def build(
        self, values: ValuesManager = None
    ) -> Union[str, Tuple[str, ValuesManager]]:
        return_values = values is None
        if not values:
            values = ValuesManager()
        result = (
            f"{'(' if self.parenthesis else ''}"
            f"{(values.add(self.first) if not isinstance(self.first, Operator) else self.first.build(values)) + ' ' if not self.no_first else ''}"
            f"{self.operator} "
            f"{values.add(self.second) if not isinstance(self.second, Operator) else self.second.build(values)}"
            f"{')' if self.parenthesis else ''}"
        )
        if return_values:
            return result, values
        else:
            return result

    def check_type(self, other):
        pass

    def __and__(self, other):
        return Operator(self, "AND", other, True)

    def __or__(self, other):
        return Operator(self, "OR", other, True)

    def __invert__(self):
        return Operator("", "NOT", self, no_first=True)

    def __eq__(self, other):
        self.check_type(other)
        return Operator(self, "=", other)

    def __ne__(self, other):
        self.check_type(other)
        return Operator(self, "!=", other)

    def __lt__(self, other):
        self.check_type(other)
        return Operator(self, "<", other)

    def __le__(self, other):
        self.check_type(other)
        return Operator(self, "<=", other)

    def __gt__(self, other):
        self.check_type(other)
        return Operator(self, ">", other)

    def __ge__(self, other):
        self.check_type(other)
        return Operator(self, ">=", other)

    def __rshift__(self, other):
        self.check_type(other)
        return Operator(self, "LIKE", other)

    def __lshift__(self, other):
        self.check_type(other)
        return Operator(self, "ILIKE", other)

    def __getitem__(self, other):
        self.check_type(other)
        return Operator(other, "IN", self)

    def __floordiv__(self, other):
        self.check_type(other)
        return Operator(self, "SIMILAR TO", other)

    def __sub__(self, other):
        self.check_type(other)
        return Operator(self, "-", other)

    def __add__(self, other):
        self.check_type(other)
        return Operator(self, "+", other)

    def __mul__(self, other):
        self.check_type(other)
        return Operator(self, "*", other)

    def __truediv__(self, other):
        self.check_type(other)
        return Operator(self, "/", other)

    def __mod__(self, other):
        self.check_type(other)
        return Operator(self, "%", other)

    def __pow__(self, other):
        self.check_type(other)
        return Operator(self, "^", other)

    def __neg__(self):
        return Operator("", "-", self, no_first=True)


class DatabaseType(Operator):
    def __init__(
        self, expected_type: Type, database_type: str, id_status: bool = False,  check: Callable[[Any], bool] = None
    ):
        super().__init__(self, "", None)
        self._expected_type = expected_type
        self._database_type = database_type
        self._primary_key = False
        self.id_status = id_status
        self._table = None
        self._name = None
        self._default = None
        self._check = check

    def clone(self) -> "DatabaseType":
        return DatabaseType(self._expected_type, self._database_type, self.id_status)

    def __getitem__(self, item) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type}[{item}]"
        return new

    def check(self, check: Callable[[Any], bool]) -> "DatabaseType":
        new = self.clone()
        new._check = check
        return new

    def check_value(self, value):
        if self._check and not self._check(value):
            raise ValueError(f"Value {value} is not valid for {self._name}")

    @property
    def array(self) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type}[]"
        return new

    @property
    def unique(self) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type} UNIQUE"
        return new

    @property
    def not_null(self) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type} NOT NULL"
        return new

    def default(self, value: Any) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type} DEFAULT {value}"
        return new

    def custom(self, custom: Callable[[str], str]) -> "DatabaseType":
        new = self.clone()
        new._database_type = custom(self._database_type)
        return new

    def __call__(self, size: int) -> "DatabaseType":
        new = self.clone()
        new._database_type = f"{self._database_type}({size})"
        return new

    def initialize(self, table: str, name: str, default: Any = None) -> "DatabaseType":
        new = self.clone()
        new._primary_key = self._primary_key
        new._check = self._check
        new._table = table
        new._name = name
        new._default = default
        return new

    def get_db_type(self):
        return (
            f"{self._database_type} PRIMARY KEY"
            if self._primary_key
            else self._database_type
        )

    def get_default(self):
        return self._default() if callable(self._default) else self._default

    def has_default(self):
        return self._default is not None

    @property
    def primary_key(self) -> "DatabaseType":
        new = self.clone()
        new._primary_key = True
        new.id_status = True
        return new

    @property
    def id(self) -> "DatabaseType":
        new = self.clone()
        new.id_status = True
        return new

    def build(self, _: ValuesManager = None) -> Union[str, Tuple[str, List[Any]]]:
        return f"{self._table}.{self._name}"

    def get_name(self):
        return self._name

    def check_type(self, other):
        if not self._table:
            raise LookupError("Type not initialized")
        if not (
            isinstance(other, self._expected_type)
            or isinstance(other, Operator)
            or (self._expected_type in [int, float] and type(other) in [int, float])
        ):
            raise TypeError(
                f"Cannot compare {self._expected_type.__name__} with {type(other).__name__}"
            )
