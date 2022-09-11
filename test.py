from src.model import Serial, Text, Int, Float, Varchar
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

    print(await User.fetch())


asyncio.run(main())
