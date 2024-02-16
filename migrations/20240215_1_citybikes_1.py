"""
create edl table
"""

from yoyo import step

__depends__ = {"20240205_1_citybikes_2"}

steps = [
    step(
        """
        ALTER TABLE citybikes.networks

        ADD COLUMN company_formatted text,
        ADD COLUMN location_city text,
        ADD COLUMN location_country text,
        ADD COLUMN location_latitude text,
        ADD COLUMN location_longitude text

        """
    )
]
