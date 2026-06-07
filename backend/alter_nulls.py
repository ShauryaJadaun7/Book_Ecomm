# bhai tu bhi isko run kardena , kyuki datbase me update karne ka reh gaya tha 
# ye not null constraint area and pincode ke liye , uske bina login hi nahi ho raha tha , 
# but jab google se karte he to possible nahi he to us vajah se 
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

engine = create_async_engine(db_url)

async def run():
    async with engine.begin() as conn:
        await conn.execute(text('ALTER TABLE users ALTER COLUMN area DROP NOT NULL;'))
        await conn.execute(text('ALTER TABLE users ALTER COLUMN pincode DROP NOT NULL;'))
    print('Done!')

asyncio.run(run())
