"""
create edl table
"""

from yoyo import step

__depends__ = {"20240205_1_citybikes_1"}

steps = [
    step(
        """
        CREATE TABLE citybikes.citybikesedl2
        (
            responsejson jsonb,
            messagesent text
        )
        """,
        "DROP TABLE citybikes.citybikesedl2",
    ),
    step(
        """
        CREATE TABLE citybikes.networkraw
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
            dateAdded timestamp default current_timestamp
        )
        """,
        "DROP TABLE citybikes.networkraw",
    ),
    step(
        """
        CREATE TABLE citybikes.stationraw
        (         
            id text,
            name text,
            extra text,
            latitude text,
            longitude text,
            timestamp text,
            free_bikes int,
            empty_slots int,
            network text,
            dateAdded timestamp default current_timestamp
        )
        """,
        "DROP TABLE citybikes.stationraw",
    ),
]


#   curs.execute("CREATE TABLE IF NOT EXISTS citybikesedl2 (responsejson jsonb, messagesent char);")
