import asyncio
import struct
import os
import aiomysql
from bleak import BleakClient

# Lisää bluetooth laitteesi mac osoite sekä palvelun uuid ja sen lisäksi databasen speksit käyttääksesi tätä koodia rasperry piillä.

ADDRESS = ""
CHARACTERISTIC_UUID = ""

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

async def handle_notification(sender, data, pool):
    values = struct.unpack('<HHH', data) # Pura kolme uint16 arvoa
    print(f"Ilmoitus {sender}: {values}") # Tulosta saadut arvot
    async with pool.acquire() as conn: # Yhdistä tietokantaan
        async with conn.cursor() as cur: # Luo kursori, jolla on metodit esim insert data
            try: # Yritä suorittaa tietokantakysely
                await cur.execute(
                    "INSERT INTO rawdata (sensorvalue_a, sensorvalue_b, sensorvalue_c, suunta) VALUES (%s,%s,%s,%s)",values) # Suorita insert-kysely
                await conn.commit() # Tallenna muutokset
            except Exception as e: # Jos tulee virhe
                print("DB virhe:", e) # Tulosta virhe

async def main():
    pool = await aiomysql.create_pool(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME) # luodaan tietokantayhteyspoolin
    try:
        async with BleakClient(ADDRESS) as client: # Yhdistä BLE laitteeseen
            print(f"Yhdistetty laitteeseen {ADDRESS}") # Ilmoita yhdistämisestä ja laitteen osoite
            await client.start_notify(CHARACTERISTIC_UUID, lambda s, d: asyncio.create_task(handle_notification(s, d, pool))) # Aloita ilmoitusten kuuntelu
            print("Ilmoitukset tilattu. Kuunnellaan...") # Ilmoita, että kuuntelu on alkanut
            while True: # ikuinen looppi
                await asyncio.sleep(1) # odota 1 sekunti
    except Exception as e: # Jos tulee virhe
        print("Virhe:", e) # Tulosta virhe

asyncio.run(main()) # Tässä juostaan koko main ohjelma
