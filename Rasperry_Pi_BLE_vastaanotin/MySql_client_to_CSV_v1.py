import asyncio
import datetime as dt
import aiomysql
import os
from dotenv import load_dotenv
import pandas as pd

HOST = os.getenv("DB_HOST_RPI")  # The server's hostname or IP address
PORT = 3306  # The port used by the server
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "temp", ".env"))
user = os.getenv("DB_USER_RPI")
password = os.getenv("DB_PASSWORD_RPI")

async def get_data():
    pool = await aiomysql.create_pool(host= HOST, user=user, password=password, db="measurements") # luodaan tietokantayhteyspoolin
    async with pool.acquire() as conn: # Yhdistä tietokantaan
        async with conn.cursor() as cur: # Luo kursori, jolla on metodit esim insert data
            try: # Yritä suorittaa tietokantakysely
                await cur.execute(
                    "SELECT timestamp, id, sensorvalue_a, sensorvalue_b, sensorvalue_c from rawdata;") # Suorita kysely
                rows = await cur.fetchall() # Hae kaikki rivit
                for row in rows: # käydään for loopilla läpi ja printtaillaan
                    ts = row[0]  # timestamp-kenttä (datetime-objekti)
                    formatted_ts = ts.strftime("%d.%m.%Y klo %H:%M:%S")  # esim. 12.11.2025 klo 13:46:35
                    print(f"Aika: {formatted_ts}, ID: {row[1]}, X: {row[2]}, Y: {row[3]}, Z: {row[4]}")
                    # Muunna rivit dict-listaksi
                    data = [
                           {
                                "timestamp": r[0].strftime("%d.%m.%Y %H:%M:%S"),
                                "id": r[1],
                                "sensorvalue_a": r[2],
                                "sensorvalue_b": r[3],
                                "sensorvalue_c": r[4]
                            }
                            for r in rows
                            ]

                    df = pd.DataFrame(data)
                    df.to_csv("data_export.csv", index=False, sep=";")  # Tallenna CSV-tiedostoon
                    print("Data tallennettu data_export.csv tiedostoon.")

            except Exception as e: # Jos tulee virhe
                print("DB virhe:", e) # Tulosta virhe
    
        pool.close() # Sulje yhteys tietokantaan
    await pool.wait_closed()



asyncio.run(get_data())

