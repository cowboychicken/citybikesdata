#!/bin/sh

WAREHOUSE_USER=postgres1 WAREHOUSE_PASSWORD=Password1 WAREHOUSE_DB=citybikes WAREHOUSE_HOST=warehouse WAREHOUSE_PORT=5432  PYTHONPATH=/code/src /usr/local/bin/python /code/src/citybikesdata/transform.py