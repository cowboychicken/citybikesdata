"""
create edl table
"""

from yoyo import step

__depends__ = {"20240205_1_citybikes_1"}

steps = [
    step(
        """
        CREATE TABLE citybikes.edl
        (
            responsejson jsonb,
            messagesent text,
            processed boolean NOT NULL DEFAULT FALSE;
            dateAdded timestamp DEFAULT current_timestamp
        )
        """,
        "DROP TABLE citybikes.edl",
    ),
    step(
        """
        CREATE TABLE citybikes.networks
        (
            id text, 
            href text,
            name text,
            company text,
            location text,
            source text,
            gbfs_href text,
            license text,
            ebikes text,
            dateApiCalled timestamp,
            dateAdded timestamp DEFAULT current_timestamp,
            unique(id)
        )
        """,
        "DROP TABLE citybikes.networks",
    ),
    step(
        """
        CREATE TABLE citybikes.stations
        (         
            id text,
            name text,
            extra text,
            latitude float,
            longitude float,
            timestamp timestamp,
            free_bikes int,
            empty_slots int,
            network text,
            dateApiCalled timestamp,
            dateAdded timestamp DEFAULT current_timestamp
        )
        """,
        "DROP TABLE citybikes.stations",
    )
]


#   curs.execute("CREATE TABLE IF NOT EXISTS citybikesedl2 (responsejson jsonb, messagesent char);")
