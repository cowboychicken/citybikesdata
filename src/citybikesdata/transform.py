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
def networks_in_edw():
    columns = [
        'id',
        'href',
        'name',
        'company',
        'company_formatted',
        'location',
        'location_city',
        'location_country',
        'location_latitude',
        'location_longitude',
        'source',
        'gbfs_href',
        'license',
        'ebikes',
        'dateApiCalled',
        'dateAdded',
    ]
    query_results = None
    with DBConnection(db_creds()).conn as conn:
        try:
            with conn.cursor() as curs:
                curs.execute(
                    "SELECT " + ','.join(columns) + " FROM citybikes.networks;"
                )
                query_results = curs.fetchall()
        except Exception as e:
            print(logging.error(traceback.format_exc()))

    df_networks = pd.DataFrame(query_results, columns=columns)
    df_networks = df_networks[
        [
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
    ]

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
        with DBConnection(db_creds()).conn as conn:
            try:
                with conn.cursor() as curs:
                    query_string = (
                        "INSERT INTO citybikes.networks ("
                        + df_networks_columns
                        + ") VALUES %s ON CONFLICT(id) DO UPDATE SET company_formatted=EXCLUDED.company_formatted, location_city=EXCLUDED.location_city, location_country=EXCLUDED.location_country, location_latitude=EXCLUDED.location_latitude, location_longitude=EXCLUDED.location_longitude;"
                    )
                    curs.execute(query_string, (row,))
            except Exception as e:
                print(logging.error(traceback.format_exc()))
    print(
        "[transform.networks_in_edw()] 'company' and 'location' formatting complete."
    )


def run():
    networks_in_edw()


if __name__ == "__main__":
    run()
