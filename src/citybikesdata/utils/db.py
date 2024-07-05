from dataclasses import dataclass

import psycopg2


@dataclass
class DBInfo:
    db: str
    user: str
    password: str
    host: str
    port: int = 5432  # default port = 5432


class DBConnection:
    def __init__(self, db_info: DBInfo):
        self.conn_string = (
            f'postgresql://{db_info.user}:{db_info.password}@'
            f'{db_info.host}:{db_info.port}/{db_info.db}'
        )
        self.conn = psycopg2.connect(self.conn_string)
