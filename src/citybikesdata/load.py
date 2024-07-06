import logging
import traceback

import pandas as pd

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


def get_updates_count(conn, message):
    query = f"SELECT count(*) FROM citybikes.edl WHERE messagesent='{message}' AND NOT processed;"
    with conn.cursor() as curs:
        curs.execute(query)
        return curs.fetchone()[0]


def fetch_updates(conn, message):
    query = f"SELECT * FROM citybikes.edl WHERE messagesent='{message}' AND NOT processed limit 500;"
    with conn.cursor() as curs:
        curs.execute(query)
        return curs.fetchall()


def fetch_db_data(conn, table, columns, filter):
    if filter == None:
        filter = True
    query = f"SELECT {','.join(columns)} FROM {table} WHERE {filter};"
    with conn.cursor() as curs:
        curs.execute(query)
        return pd.DataFrame(curs.fetchall(), columns=columns)


def insert_updates(df_differences, update, table):
    # if df_differences.empty: return
    tuples = [tuple(x) for x in df_differences.to_numpy()]
    df_differences_columns = ','.join(list(df_differences.columns))
    with DBConnection(db_creds()).conn as conn:
        with conn.cursor() as curs:
            for row in tuples:
                query_string = f"INSERT INTO {table} ({df_differences_columns}) VALUES %s;"
                curs.execute(query_string, (row,))
            curs.execute(
                "UPDATE citybikes.edl SET processed = TRUE WHERE id = %s",
                (update[0],),
            )


def process_network_updates(update, columns):
    df_fromjson = pd.DataFrame(update[1].get('networks'))
    # psql get query of network records

    with DBConnection(db_creds()).conn as conn:
        df_fromdb = fetch_db_data(
            conn, 'citybikes.networks', columns, filter=None
        )

    # to avoid unhashable errors
    df_fromdb = df_fromdb.astype(str)
    df_fromjson = df_fromjson.astype(str)
    #   temporary to skip empty api responses and identify id's
    if df_fromjson.empty:
        return None
    df_differences = df_fromjson.merge(df_fromdb, how='left')
    df_differences = df_differences.query('dateAdded.isnull()')
    df_differences = df_differences[df_fromjson.columns]
    df_differences['dateApiCalled'] = update[4]
    return df_differences


# Processing CityBikes EDL
def networks_to_edw():
    columns = [
        'id',
        'href',
        'name',
        'company',
        'location',
        'source',
        'gbfs_href',
        'license',
        'ebikes',
        'dateApiCalled',
        'dateAdded',
    ]

    print("[load.networks_to_edw()] querying db....")

    try:
        with DBConnection(db_creds()).conn as conn:
            networks_updates_count = get_updates_count(conn, 'networks')
    except Exception as e:
        logging.error(traceback.format_exc())
        return

    print(
        f"[load.networks_to_edw()] {networks_updates_count} updates found..."
    )
    print("[load.networks_to_edw()] looping through results from db....")
    file_count = 0

    while file_count < networks_updates_count:
        try:
            with DBConnection(db_creds()).conn as conn:
                networks_updates = fetch_updates(conn, 'networks')
        except Exception as e:
            logging.error(traceback.format_exc())
            return
        # each response == a table ENTRY/ROW, so need to choose correct index/tuple(column), then select key from resulting dict

        for update in networks_updates:
            file_count += 1
            try:
                df_differences = process_network_updates(update, columns)
                insert_updates(df_differences, update, 'citybikes.networks')
            except Exception as e:
                logging.error(traceback.format_exc())
        print(f"[load.networks_to_edw()] {file_count} files processed.")


def process_station_updates(update, columns, network):
    df_fromjson = pd.DataFrame(update[1]['network'].get('stations'))
    df_fromjson['network'] = network

    with DBConnection(db_creds()).conn as conn:
        df_fromdb = fetch_db_data(
            conn, 'citybikes.stations', columns, filter=f"network='{network}'"
        )

    # only get most recent records for each station
    df_fromdb = df_fromdb.drop_duplicates(subset=['id', 'name'], keep='last')

    # append records from json
    df_appended = pd.concat([df_fromdb, df_fromjson], ignore_index=True)

    # remove duplicates completely. (means no change since last update)
    df_appended = df_appended.drop_duplicates(
        subset=['id', 'name', 'free_bikes', 'empty_slots'], keep=False
    )
    # isolate record from json. (dateAdded is added by DB)
    df_differences = df_appended.query('dateAdded.isnull()')
    df_differences = df_differences[df_fromjson.columns]
    df_differences['extra'] = df_differences['extra'].astype(str)
    df_differences['dateApiCalled'] = update[4]  # adding third column from edl
    return df_differences


def station_to_edw(network):
    columns = [
        'id',
        'name',
        'extra',
        'latitude',
        'longitude',
        'timestamp',
        'free_bikes',
        'empty_slots',
        'network',
        'dateApiCalled',
        'dateAdded',
    ]
    print("[load.stations_to_edw()] querying db....")
    try:
        with DBConnection(db_creds()).conn as conn:
            station_updates_count = get_updates_count(conn, network)
    except Exception as e:
        logging.error(traceback.format_exc())
        return

    print(f"[load.stations_to_edw()] {station_updates_count} updates found...")
    print("[load.stations_to_edw()] looping through results from db....")

    file_count = 0

    while file_count < station_updates_count:
        try:
            with DBConnection(db_creds()).conn as conn:
                station_updates = fetch_updates(conn, network)
        except Exception as e:
            logging.error(traceback.format_exc())
            return
        for update in station_updates:
            file_count += 1
            try:
                df_differences = process_station_updates(
                    update, columns, network
                )
                insert_updates(df_differences, update, 'citybikes.stations')
            except Exception as e:
                logging.error(traceback.format_exc())
        print(f"[load.stations_to_edw()] {file_count} files processed.")


def run():
    networks_to_edw()
    station_to_edw('fortworth')
    station_to_edw('austin')
    station_to_edw('houston')
    station_to_edw('elpaso')
    station_to_edw('sanantonio')
    station_to_edw('mcallen')
    

if __name__ == "__main__":
    run()
