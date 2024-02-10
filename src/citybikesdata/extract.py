import requests
import logging
import traceback
import json

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds


url = "https://api.citybik.es/v2/networks"


def get_networks():
    try:
        response = requests.request('get', url)
    except requests.ConnectionError as ce:
        logging.error(f"There was an error with the request, {ce}")
    return response.json()


def get_stations_for(network_id):
    try:
        response = requests.request('get', url + "/" + network_id)
    except requests.ConnectionError as ce:
        logging.error(f"There was an error with the request, {ce}")
    return response.json()


def main():
    with DBConnection(db_creds()).conn as conn:
        try:
            with conn.cursor() as curs:
                curs.execute("INSERT INTO citybikes.citybikesedl2 (responsejson, messagesent) VALUES (%s, %s)", (json.dumps(get_networks()),"networks" ))
                curs.execute("INSERT INTO citybikes.citybikesedl2 (responsejson, messagesent) VALUES (%s, %s)", (json.dumps(get_stations_for("fortworth")),"fortworth" ))
        except Exception as e:
            print(logging.error(traceback.format_exc()))


if __name__ == "__main__":
    main()
