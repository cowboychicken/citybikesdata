DE project using Citybikes API 

Infrastructure and Tools:
    - Airflow
    - Docker
    - Pandas
    - Metabase
    - AWS ec2
    - Terraform
    - Github Actions


Future Work:
 - Pass in db credentials using env variables for cron scripts
 - Add db back up and rebuild functionality (dump,migration)
 - Fix pipelinerunner container logs
 - Clean up etl scripts to output better logs



Immediate To-Do:
    - ETL
        - flatten location column 
        - Clean up data - parse/trim, replace nan's, 
        - Convert lat/long to float types
        - make new migration to alter table with new columns from transformations
        - make etl scripts so that log shows errors. currently will not record anything if any scripts break
        

