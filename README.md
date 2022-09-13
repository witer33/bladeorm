# BladeORM
A light & tiny ORM for PostgreSQL, built for ease of use.
# Installation
```bash
pip3 install bladeorm
```
# Example
```python3
from bladeorm.model import Text, Int, Varchar
from bladeorm.client import Client
import asyncio


client = Client()


@client.model
class User:

    name: Varchar(20).primary_key
    last_name: Text
    age: Int


async def main():
    await client.start("postgresql://postgres:postgres@localhost:5432/postgres")
    await client.create_tables()

    await User(name="John", last_name="Doe", age=20).save()

    user = await User(User.name == "John")
    user.age += 1
    await user.save()

    await User(User.age > 10).update(age=User.age / 2 * 2.5)

    name, age = await User(User.name == "John").fetchone(User.name, User.age)


asyncio.run(main())

```
# Documentation
## Types
### Available types
| BladeORM        | SQL              | Python        |
|-----------------|------------------|---------------|
| Text            | TEXT             | str           |
| Varchar(length) | VARCHAR(length)  | str           |
| SmallInt        | SMALLINT         | int           |
| Int             | INTEGER          | int           |
| BigInt          | BIGINT           | int           |
| Float           | DOUBLE PRECISION | float         |
| Bool            | BOOLEAN          | bool          |
| SmallSerial     | SMALLSERIAL      | int           |
| Serial          | SERIAL           | int           |
| BigSerial       | BIGSERIAL        | int           |
| Date            | DATE             | datetime.date |
### Type modifiers
| BladeORM                               | SQL           | Details                                                                                                         |
|----------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------|
| .primary_key                           | PRIMARY KEY   |                                                                                                                 |
| .unique                                | UNIQUE        |                                                                                                                 |
| .not_null                              | NOT NULL      |                                                                                                                 |
| .default(value)                        | DEFAULT value | NOT SQLI SAFE                                                                                                   |
| .custom(lambda current_type: new_type) | //            | Directly modify the type                                                                                        |
| .id                                    | //            | Use as ID without setting primary key                                                                           |
| .array                                 | TYPE[]        |                                                                                                                 |
| type[length]                           | TYPE[length]  |                                                                                                                 |
| = default                              | //            | Ex.: name: Text = "John", set the default value, but it's directly managed by BladeORM.                         |
| = lambda: default                      | //            | Ex.: name: Text = lambda: "John", set the default value with a callable, but it's directly managed by BladeORM. |
| .check(lambda value : value > 0)       | //            | Add a check constraint managed by BladeORM.                                                                     |
## Querying
### Fetch
```python3
await User(User.age + 10 > 20).fetch() -> List[User]
```
### Fetchone
```python3
await User(User.age + 10 > 20).fetchone() -> User
```
### Update
```python3
await User(User.age + 10 > 20).update(age=User.age - 5.2)
```
### Delete
```python3
await User(User.age + 10 > 20).delete()
```
## Conditions
| BladeORM            | SQL                   |
|---------------------|-----------------------|
| User.name == "John" | name = 'John'         |
| User.name != "John" | name != 'John'        |
| User.age > 20       | age > 20              |
| User.age >= 20      | age >= 20             |
| User.age < 20       | age < 20              |
| User.age <= 20      | age <= 20             |
| User.name // "%a%"  | name SIMILAR TO '%a%' |
| User.name >> "%a%"  | name LIKE '%a%'       |
| User.name << "%a%"  | name ILIKE '%a%'      |
| User.names[“John”]  | 'John' IN names       |