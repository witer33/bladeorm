from src.model import Text, Int, Varchar
from src.client import Client
import asyncio


client = Client()


@client.model
class User:

    name: Varchar(20).primary_key
    last_names: Text
    age: Int


async def main():
    await client.start("postgresql://postgres:postgres@localhost:5432/postgres")
    await client.create_tables()

    await User(name="John", last_names="Doe", age=20).save()

    print(await User(User.name == "John").fetchone())

    print(await User(User.age > 10).update(age=User.age / 2 * 2.5))


asyncio.run(main())
