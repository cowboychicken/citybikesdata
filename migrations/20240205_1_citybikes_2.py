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
            dateAdded timestamp default current_timestamp
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
            company_formatted text,
            location text,
            location_city text,
            location_country text,
            location_latitude text,
            location_longitude text,
            source text,
            gbfs_href text,
            license text,
            ebikes text,
            dateApiCalled timestamp,
            dateAdded timestamp default current_timestamp,
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
            dateAdded timestamp default current_timestamp
        )
        """,
        "DROP TABLE citybikes.stations",
    ),
]


#   curs.execute("CREATE TABLE IF NOT EXISTS citybikesedl2 (responsejson jsonb, messagesent char);")
