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
    query = f"SELECT id,responsejson,dateAdded FROM citybikes.edl WHERE messagesent='{message}' AND NOT processed ORDER BY dateadded ASC limit 500  ;"
    with conn.cursor() as curs:
        curs.execute(query)
        return curs.fetchall()


def fetch_db_data(conn, table, columns, filter):
    if filter is None:
        filter = True
    query = f"SELECT {','.join(columns)} FROM {table} WHERE {filter};"
    with conn.cursor() as curs:
        curs.execute(query)
        return pd.DataFrame(curs.fetchall(), columns=columns)


def fetch_station_db_data(conn, table, columns, filter):
    if filter is None:
        filter = True
    query = f"SELECT s1.id, s2.free_bikes, s2.empty_slots FROM (SELECT id,max(dateApiCalled) as maxdate FROM citybikes.stations WHERE {filter} GROUP BY id) as s1 LEFT JOIN citybikes.stations as s2 ON s1.id=s2.id AND s1.maxdate=s2.dateApiCalled;"
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
    df_differences['dateApiCalled'] = update[2]
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
    except Exception:
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
        except Exception:
            logging.error(traceback.format_exc())
            return
        # each response == a table ENTRY/ROW, so need to choose correct index/tuple(column), then select key from resulting dict
        for update in networks_updates:
            file_count += 1
            try:
                df_differences = process_network_updates(update, columns)
                insert_updates(df_differences, update, 'citybikes.networks')
            except Exception:
                logging.error(traceback.format_exc())
        print(f"[load.networks_to_edw()] {file_count} files processed.")


def process_station_updates(update, columns, network):
    # get new json, compare to db
    # return differences, if any

    # gets list of last update, for each (station,network)
    with DBConnection(db_creds()).conn as conn:
        df_fromdb2 = fetch_station_db_data(
            conn, 'citybikes.stations', columns, filter=f"network='{network}'"
        )

    # parse json for 'station' info then left join with db results
    df_fromjson = pd.DataFrame(update[1]['network'].get('stations'))
    df_fromjson = df_fromjson.merge(df_fromdb2, how="left", on='id')

    # remove rows that show no change since last update
    df_differences = df_fromjson[
        (df_fromjson.free_bikes_x != df_fromjson.free_bikes_y)
        | (df_fromjson.empty_slots_x != df_fromjson.empty_slots_y)
    ]

    df_differences = df_differences.rename(
        columns={'free_bikes_x': 'free_bikes', 'empty_slots_x': 'empty_slots'}
    )
    df_differences = df_differences[df_fromdb2.columns]

    # Add metadata
    if df_differences.empty is False:
        df_differences['network'] = network
        df_differences['dateApiCalled'] = update[2]
    return df_differences


def station_to_edw(network):
    columns = [
        'id',
        'free_bikes',
        'empty_slots',
    ]

    print(f"[load.stations_to_edw({network})] querying db....")
    try:
        with DBConnection(db_creds()).conn as conn:
            station_updates_count = get_updates_count(conn, network)
    except Exception:
        logging.error(traceback.format_exc())
        return

    print(
        f"[load.stations_to_edw({network})] {station_updates_count} updates found..."
    )
    print(
        f"[load.stations_to_edw({network})] looping through results from db...."
    )

    file_count = 0

    while file_count < station_updates_count:
        # while file_count == 0:
        try:
            with DBConnection(db_creds()).conn as conn:
                station_updates = fetch_updates(conn, network)
        except Exception:
            logging.error(traceback.format_exc())
            return
        for update in station_updates:
            file_count += 1
            try:
                df_differences = process_station_updates(
                    update, columns, network
                )

                insert_updates(
                    df_differences, update, table='citybikes.stations'
                )
            except Exception:
                logging.error(traceback.format_exc())
        print(
            f"[load.stations_to_edw({network})] {file_count} files processed."
        )


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
