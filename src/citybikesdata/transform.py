import logging
import traceback

import pandas as pd

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


# Processing CityBikes EDL 
def load_network_data_to_edw():

    networks_updates = None
    with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM citybikes.citybikesedl2 WHERE messagesent='networks';")
                    networks_updates = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

    # response == a DB ENTRY, so need to choose correct index/tuple(column), then select key from resulting dict
    for update in networks_updates:

        df_fromjson = pd.DataFrame(update[0].get('networks'))

        # psql get query of network records
        db_query_results = None
        with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM citybikes.networkraw;")
                    db_query_results = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

        df_fromdb = pd.DataFrame(db_query_results, columns=['id','href','name','company','location','source','gbfs_href','license','ebikes','dateAdded'])

        # to avoid unhashable errors
        df_fromdb = df_fromdb.astype(str)
        df_fromjson = df_fromjson.astype(str)

        df_differences = df_fromjson.merge(df_fromdb, how='left')

        df_differences = df_differences.query('dateAdded.isnull()')
        df_differences = df_differences[df_fromjson.columns]

        tuples = [tuple(x) for x in df_differences.to_numpy()]
        columns = ','.join(list(df_differences.columns))

        print("columns")
        print(columns)
        print('\n\n')
        for row in tuples:
            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        query_string = "INSERT INTO citybikes.networkraw (" + columns + ") VALUES %s;"
                        curs.execute(query_string, (row,))
                except Exception as e:
                    print(logging.error(traceback.format_exc()))


def load_station_data_to_edw():
    station_updates = None 
    with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM citybikes.citybikesedl2 WHERE messagesent='fortworth';")
                    station_updates = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

    print ("starting station transformations......") 
    for update in station_updates:
        df_fromjson = pd.DataFrame(update[0]['network'].get('stations'))
        df_fromjson['network'] = 'fortworth'

        db_query_results = None

        with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM citybikes.stationraw;")
                    db_query_results = curs.fetchall()
            except Exception as e:
                print(logging.error(traceback.format_exc()))

        df_fromdb = pd.DataFrame(db_query_results, columns=['id', 'name', 'extra', 'latitude','longitude','timestamp','free_bikes','empty_slots','network','dateAdded'])

        #only get most recent records for each station
        df_fromdb = df_fromdb.drop_duplicates(subset=['id','name'], keep='last')

        # append records from json
        df_appended = pd.concat([df_fromdb, df_fromjson], ignore_index=True)

        # remove duplicates completely. (means no change since last update)
        df_appended = df_appended.drop_duplicates(subset=['id','name','free_bikes','empty_slots'],keep=False)
        # isolate record from json. (dateAdded is added by DB)
        df_differences = df_appended.query('dateAdded.isnull()')
        df_differences = df_differences[df_fromjson.columns]
        df_differences['extra'] = df_differences['extra'].astype(str)

        tuples = [tuple(x) for x in df_differences.to_numpy()]

        columns = ','.join(list(df_differences.columns))
        for row in tuples:
            with DBConnection(db_creds()).conn as conn:
                try:
                    with conn.cursor() as curs:
                        query_string = "INSERT INTO citybikes.stationraw (" + columns + ") VALUES %s;"
                        curs.execute(query_string, (row,))
                except Exception as e:
                    print(logging.error(traceback.format_exc()))

def main():
    load_network_data_to_edw()
    load_station_data_to_edw()

if __name__ == "__main__":
    main()
    print("YO")