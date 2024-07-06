import json
import logging
import traceback

import requests

from citybikesdata.utils.db import DBConnection
from citybikesdata.utils.db_config import get_db_creds as db_creds

# Main API Endpoint
API_URL = "https://api.citybik.es/v2/networks"


def send_api_request(request):
    try:
        response = requests.request('get', request)
        print("response", type(response))
    except requests.ConnectionError as ce:
        logging.error(f"There was an error with the request, {ce}")
    return response


def get_networks() -> json:
    return send_api_request(API_URL).json()


def get_stations_for(network_id) -> json:
    return send_api_request(API_URL + "/" + network_id).json()


def load_response_to_edl(response: json, request: str):
    with DBConnection(db_creds()).conn as conn:
        try:
            with conn.cursor() as curs:
                curs.execute(
                    "INSERT INTO citybikes.edl (responsejson, messagesent) VALUES (%s, %s)",
                    (json.dumps(response), request),
                )
        except Exception as e:
            print(logging.error(traceback.format_exc()))


if __name__ == "__main__":
    load_response_to_edl(get_networks(), "networks")
    load_response_to_edl(get_stations_for("fortworth"), "fortworth")
    load_response_to_edl(get_stations_for("austin"), "austin")
