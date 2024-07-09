import ast
import logging
import traceback

import pandas as pd

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


#   Networks transform requirements:
#       - remove brackets and quotes from 'company'. EX) ['MyCompanyName'] -- > MyCompanyName
#       - split up 'location' EX) {'city': 'Moscow', 'country': 'RU', 'latitude': 55.75, 'longitude': 37.616667}
#           into 'city' ,'country', 'latitude', 'longitude'


def fetch_db_data(conn, table, columns, filter):
    if filter == None:
        filter = True
    query = f"SELECT {','.join(columns)} FROM {table} WHERE {filter};"
    with conn.cursor() as curs:
        curs.execute(query)
        return pd.DataFrame(curs.fetchall(), columns=columns)

def stations_in_edw():

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

    try:
        with DBConnection(db_creds()).conn as conn:
            df_stations = fetch_db_data(conn, 'citybikes.stations', columns, filter="timestamp_custom_bin_hour is null")
    except Exception as e:
        logging.error(traceback.format_exc())
    print("YO")
    print(f"[transform.stations_in_edw()] df_stations.count = {df_stations.count}")


    # Add bin for timestamp 
    tz_offset = 5
    df_stations['timestamp_custom_bin_hour'] = (df_stations['timestamp'].dt.hour - tz_offset) % 24

    print("[transform.stations_in_edw()] df_stations.'timestamp_custom_bin_hour' = \n", df_stations[['timestamp','timestamp_custom_bin_hour']])

     # upsert records
    tuples = [tuple(x) for x in df_stations.to_numpy()]
    df_stations_columns = ','.join(list(df_stations.columns))
    for row in tuples:
        try:
            with DBConnection(db_creds()).conn as conn:
                with conn.cursor() as curs:
                    #query_string = f"INSERT INTO citybikes.networks ({df_networks_columns}) VALUES %s ON CONFLICT(id) DO UPDATE SET company_formatted=EXCLUDED.company_formatted, location_city=EXCLUDED.location_city, location_country=EXCLUDED.location_country, location_latitude=EXCLUDED.location_latitude, location_longitude=EXCLUDED.location_longitude;"
                    query_string = f"INSERT INTO citybikes.stations ({df_stations_columns}) VALUES %s ON CONFLICT(id,timestamp) DO UPDATE SET timestamp_custom_bin_hour=EXCLUDED.timestamp_custom_bin_hour;"
                    curs.execute(query_string, (row,))
        except Exception as e:
            logging.error(traceback.format_exc())
            return



def networks_in_edw():
    
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

    try:
        with DBConnection(db_creds()).conn as conn:
            df_networks = fetch_db_data(
                conn, 'citybikes.networks', columns, filter=None
            )
    except Exception as e:
        logging.error(traceback.format_exc())

    print(f"[transform.networks_in_edw()] df_networks.count = {df_networks.count}")

    # clean company column
    df_networks['company_formatted'] = df_networks['company'].map(
        lambda x: x.lstrip("['").rstrip("']")
    )

    # split 'location' json
    split_location = pd.json_normalize(
        df_networks['location'].apply(ast.literal_eval).tolist()
    ).add_prefix('location_')
    df_networks = df_networks.join([split_location])

    # upsert records
    tuples = [tuple(x) for x in df_networks.to_numpy()]
    df_networks_columns = ','.join(list(df_networks.columns))
    for row in tuples:
        try:
            with DBConnection(db_creds()).conn as conn:
                with conn.cursor() as curs:
                    #query_string = f"INSERT INTO citybikes.networks ({df_networks_columns}) VALUES %s ON CONFLICT(id) DO UPDATE SET company_formatted=EXCLUDED.company_formatted, location_city=EXCLUDED.location_city, location_country=EXCLUDED.location_country, location_latitude=EXCLUDED.location_latitude, location_longitude=EXCLUDED.location_longitude;"
                    query_string = f"INSERT INTO citybikes.networks ({df_networks_columns}) VALUES %s ON CONFLICT(id,dateAdded) DO UPDATE SET company_formatted=EXCLUDED.company_formatted;"
                    curs.execute(query_string, (row,))
        except Exception as e:
            logging.error(traceback.format_exc())
            return


    print(
        "[transform.networks_in_edw()] 'company' and 'location' formatting complete."
    )


def run():
    networks_in_edw()
    stations_in_edw()

if __name__ == "__main__":
    run()
