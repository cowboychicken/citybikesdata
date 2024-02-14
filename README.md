DE project using Citybikes API 

Tools:
    - Airflow
    - Docker
    - Pandas
    - Metabase
    - Terraform / AWS ec2


Immediate To-Do:
    - ETL
        - flatten location column 
        - Clean up data - parse/trim, replace nan's, 
        - Convert lat/long to number types

    - DB Schema
        - Add date-proccessed to edl

Future Work:
 - Pass in db credentials using env variables for cron scripts
 - Add db back up and rebuild functionality (dump,migration)
 - Fix pipelinerunner container logs
 - Clean up etl scripts to output better logs



