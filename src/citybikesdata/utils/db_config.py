import os

from citybikesdata.utils.db import DBInfo


def get_db_creds() -> DBInfo:
    return DBInfo(
        user=os.getenv('WAREHOUSE_USER', ''),
        password=os.getenv('WAREHOUSE_PASSWORD', ''),
        db=os.getenv('WAREHOUSE_DB', ''),
        host=os.getenv('WAREHOUSE_HOST', ''),
        port=int(os.getenv('WAREHOUSE_PORT', 5432)),
    )
