# bladeorm
A tiny light ORM for PostgreSQL, built for ease of use.
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

    print(await User(User.name == "John").fetchone())

    print(await User(User.age > 10).update(age=User.age / 2 * 2.5))


asyncio.run(main())

```
# Documentation
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