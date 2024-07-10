import logging
import traceback

import pandas as pd

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


def fetch_updates(conn, message):
    query = f"SELECT id,responsejson,dateAdded FROM citybikes.edl WHERE messagesent='{message}' AND NOT processed ORDER BY dateadded ASC limit 500  ;"
    with conn.cursor() as curs:
        curs.execute(query)
        return curs.fetchall()


def stationinfo_to_edw(network):
    columns = ['id', 'name', 'latitude', 'longitude']

    print("[load.stationinfo_to_edw()] querying db....")

    try:
        with DBConnection(db_creds()).conn as conn:
            station_updates = fetch_updates(conn, network)
            query = f"SELECT responsejson,dateAdded FROM citybikes.edl WHERE messagesent='{network}' ORDER BY dateadded DESC limit 1;"
            with conn.cursor() as curs:
                curs.execute(query)
                station_updates = curs.fetchall()
    except Exception as e:
        logging.error(traceback.format_exc())
        return

    try:
        with DBConnection(db_creds()).conn as conn:
            query = f"SELECT {','.join(columns)} FROM citybikes.station_info WHERE network='{network}';"
            with conn.cursor() as curs:
                curs.execute(query)
                df_fromdb = pd.DataFrame(curs.fetchall(), columns=columns)

        df_fromjson = pd.DataFrame(
            station_updates[0][0]['network'].get('stations')
        )

        df_appended = pd.concat([df_fromdb, df_fromjson], ignore_index=True)

        df_differences = df_appended.drop_duplicates(
            subset=['id', 'name', 'latitude', 'longitude'], keep=False
        )
        df_differences = df_differences[columns]
        df_differences['network'] = network

        tuples = [tuple(x) for x in df_differences.to_numpy()]
        df_differences_columns = ','.join(list(df_differences.columns))
        with DBConnection(db_creds()).conn as conn:
            with conn.cursor() as curs:
                for row in tuples:
                    query_string = f"INSERT INTO citybikes.station_info ({df_differences_columns}) VALUES %s;"
                    curs.execute(query_string, (row,))

    except Exception as e:
        logging.error(traceback.format_exc())
    print(f"[load.stationinfo_to_edw()] 1 files processed.")


def run():
    if True:
        stationinfo_to_edw('fortworth')
        stationinfo_to_edw('austin')
        stationinfo_to_edw('houston')
        stationinfo_to_edw('elpaso')
        stationinfo_to_edw('sanantonio')
        stationinfo_to_edw('houston')


if __name__ == "__main__":
    run()
