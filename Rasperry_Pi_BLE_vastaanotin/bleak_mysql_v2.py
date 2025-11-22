import asyncio
import struct
import os
import aiomysql
from bleak import BleakClient

ADDRESS = "EC:6B:86:29:EE:5A"
CHARACTERISTIC_UUID = "00001526-1212-EFDE-1523-785FEABCD123"

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

async def handle_notification(sender, data, pool):
    values = struct.unpack('<HHHH', data)
    print(f"Ilmoitus {sender}: {values}")
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(
                    "INSERT INTO rawdata (sensorvalue_a, sensorvalue_b, sensorvalue_c, suunta) VALUES (%s,%s,%s,%s)",
                    values
                )
                await conn.commit()
            except Exception as e:
                print("DB virhe:", e)

async def main():
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)
    try:
        async with BleakClient(ADDRESS) as client:
            print(f"Yhdistetty laitteeseen {ADDRESS}")
            await client.start_notify(CHARACTERISTIC_UUID, lambda s, d: asyncio.create_task(handle_notification(s, d, pool)))
            print("Ilmoitukset tilattu. Kuunnellaan...")
            while True:
                await asyncio.sleep(1)
    except Exception as e:
        print("Virhe:", e)

asyncio.run(main())
