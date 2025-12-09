import asyncio
import datetime as dt
import aiomysql
import pandas as pd

HOST = ""  # The server's hostname or IP address
PORT =   # The port used by the server
USER = ""  # The username to authenticate with
PASSWORD = ""  # The password to authenticate with
DB = ""  # The name of the database to use

async def get_data():
    pool = await aiomysql.create_pool(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB) # luodaan tietokantayhteyspoolin, tarvitset käyttäjätunnuksen, salasanan ja tietokannan nimen
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

