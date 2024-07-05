import logging
import traceback

import pandas as pd

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


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

    networks_updates = None
    networks_updates_count = None

    print("[load.networks_to_edw()] querying db....")
    with DBConnection(db_creds()).conn as conn:
        try:
            with conn.cursor() as curs:
                curs.execute(
                    "SELECT count(*) FROM citybikes.edl WHERE messagesent='networks' AND NOT processed;"
                )
                networks_updates_count = curs.fetchone()[0]
        except Exception as e:
            print(logging.error(traceback.format_exc()))

    print(
        "[load.networks_to_edw()] ",
        networks_updates_count,
        " updates found...",
    )
    print("[load.networks_to_edw()] looping through results from db....")
    file_count = 0

    while file_count < networks_updates_count:

        with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute(
                        "SELECT * FROM citybikes.edl WHERE messagesent='networks' AND NOT processed limit 500;"
                    )
                    networks_updates = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

        # each response == a table ENTRY/ROW, so need to choose correct index/tuple(column), then select key from resulting dict
        for update in networks_updates:
            file_count += 1
            df_fromjson = pd.DataFrame(update[1].get('networks'))
            # psql get query of network records
            db_query_results = None
            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        curs.execute(
                            "SELECT "
                            + ','.join(columns)
                            + " FROM citybikes.networks;"
                        )
                        db_query_results = curs.fetchall()
                except Exception as e:
                    print(logging.error(traceback.format_exc()))

            df_fromdb = pd.DataFrame(db_query_results, columns=columns)

            # to avoid unhashable errors
            df_fromdb = df_fromdb.astype(str)
            df_fromjson = df_fromjson.astype(str)
            #   temporary to skip empty api responses and identify id's
            if df_fromjson.empty:
                continue
            df_differences = df_fromjson.merge(df_fromdb, how='left')
            df_differences = df_differences.query('dateAdded.isnull()')
            df_differences = df_differences[df_fromjson.columns]
            df_differences['dateApiCalled'] = update[4]

            tuples = [tuple(x) for x in df_differences.to_numpy()]
            df_differences_columns = ','.join(list(df_differences.columns))

            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        for row in tuples:
                            query_string = (
                                "INSERT INTO citybikes.networks ("
                                + df_differences_columns
                                + ") VALUES %s;"
                            )
                            curs.execute(query_string, (row,))
                        curs.execute(
                            "UPDATE citybikes.edl SET processed = TRUE WHERE id = %s",
                            (update[0],),
                        )
                except Exception as e:
                    print(e)
                    print(logging.error(traceback.format_exc()))

        print(
            "[load.networks_to_edw()] "
            + str(file_count)
            + " files proccessed."
        )


def station_to_edw():

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

    station_updates = None
    station_updates_count = None

    print("[load.stations_to_edw()] querying db....")
    with DBConnection(db_creds()).conn as conn:
        try:
            with conn.cursor() as curs:
                curs.execute(
                    "SELECT count(*) FROM citybikes.edl WHERE messagesent='fortworth' AND NOT processed limit 500;"
                )
                station_updates_count = curs.fetchone()[0]
        except Exception as e:
            print(logging.error(traceback.format_exc()))

    print(
        "[load.stations_to_edw()] ", station_updates_count, " updates found..."
    )
    print("[load.stations_to_edw()] looping through results from db....")
    file_count = 0

    while file_count < station_updates_count:
        with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute(
                        "SELECT * FROM citybikes.edl WHERE messagesent='fortworth' AND NOT processed limit 500;"
                    )
                    station_updates = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

        for update in station_updates:
            file_count += 1
            df_fromjson = pd.DataFrame(update[1]['network'].get('stations'))
            df_fromjson['network'] = 'fortworth'

            db_query_results = None

            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        curs.execute("SELECT * FROM citybikes.stations;")
                        db_query_results = curs.fetchall()
                except Exception as e:
                    print(logging.error(traceback.format_exc()))

            df_fromdb = pd.DataFrame(db_query_results, columns=columns)

            # only get most recent records for each station
            df_fromdb = df_fromdb.drop_duplicates(
                subset=['id', 'name'], keep='last'
            )

            # append records from json
            df_appended = pd.concat(
                [df_fromdb, df_fromjson], ignore_index=True
            )

            # remove duplicates completely. (means no change since last update)
            df_appended = df_appended.drop_duplicates(
                subset=['id', 'name', 'free_bikes', 'empty_slots'], keep=False
            )
            # isolate record from json. (dateAdded is added by DB)
            df_differences = df_appended.query('dateAdded.isnull()')
            df_differences = df_differences[df_fromjson.columns]
            df_differences['extra'] = df_differences['extra'].astype(str)
            df_differences['dateApiCalled'] = update[
                4
            ]  # adding third column from edl

            tuples = [tuple(x) for x in df_differences.to_numpy()]

            df_differences_columns = ','.join(list(df_differences.columns))
            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        for row in tuples:
                            query_string = (
                                "INSERT INTO citybikes.stations ("
                                + df_differences_columns
                                + ") VALUES %s;"
                            )
                            curs.execute(query_string, (row,))
                        curs.execute(
                            "UPDATE citybikes.edl SET processed = TRUE WHERE id = %s",
                            (update[0],),
                        )
                except Exception as e:
                    print(e)
                    print(logging.error(traceback.format_exc()))

        print(
            "[load.stations_to_edw()] "
            + str(file_count)
            + " files proccessed."
        )


def run():
    networks_to_edw()
    station_to_edw()


if __name__ == "__main__":
    run()
