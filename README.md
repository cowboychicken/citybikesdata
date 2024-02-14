DE project using Citybikes API 

Tools:
    - Airflow
    - Docker
    - Pandas
    - Metabase
    - Terraform / AWS ec2



Immediate To-Do:

    - ETL
        - change transform file name to load
        - flatten location column 
        - clean up data - parse/trim, replace nan's, 
        - convert lat/long to number types

    - DB Schema
        - add date-proccessed to edl
            OR/And add edl dateadded to edw entry to remove duplicates, or compare with 
            

        - change edl name to just edl
        


Future Work:
 - pass in db credentials for cron scripts
 - figure out way to easily back up and rebuild db (dump,migration)
 - fix pipelinerunner logs
 - clean up etl scripts to output better logs



